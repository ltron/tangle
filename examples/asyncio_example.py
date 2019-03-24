""" Example of how to drive a tangled graph using asyncio.

The foo and bar Tangled objects are setup. The source nodes
are fed with random numbers using coroutines wrapped in tasks.

The top level nodes (that depends on the source nodes) are
subscribed to. Updated values are printed whenever these top
level nodes needs to be recalculated due to a source update.
"""
import asyncio
import random

from tangle import Tangled, TreeBuilder, BasicEvaluator, tangled_function, tangled_link

Tangled.set_handlers(TreeBuilder(), BasicEvaluator())


@tangled_function
def average(a, b):
    """ Decorator ensures that this function can be used in a Tangled graph
    """
    return (a + b) / 2


class Foo(Tangled):

    # Source nodes on Foo
    source1 = TangledSource()
    source2 = TangledSource()

    # This Blueprint will build nodes that call the function average
    # defined above
    foo_value = average(source1, source2)

    def __str__(self):
        return 'Foo<Instance>'


class Bar(Tangled):

    def __init__(self, foo):
        super().__init__()
        self._foo = foo

    @tangled_link(Foo)
    def my_foo(self):
        """ The decorator is used by the TangledMapper class to find the
        link between a Bar instance and an Foo instance. This means that
        a node in Bar can reference nodes in the other class.
        """
        return self._foo

    # Define a source on Bar
    source1 = TangledSource()

    # Defines a bar Blueprint that references Blueprints on Foo. This is how
    # nodes become be dependant on nodes in other objects
    bar_value = (source1 + Foo.foo_value) / Foo.source1

    def __str__(self):
        return 'Bar<Instance>'


async def source_feeder(tangled_object, source_name):
    """ This coroutine will update a Foo or Bar source node with values at
    random intervals
    """
    for _ in range(4):
        await asyncio.sleep(random.uniform(0.5, 2))
        setattr(tangled_object, source_name, random.randint(-20, 20)/2.0)


async def print_watcher(tangled_object, node_name):
    """ A watcher of a node. It subscribes by providing an event to the
    node. If a source the node is dependent on is updated the event will
    be set and the new value is printed (and tree evaluated if required).
    """
    event = asyncio.Event()
    tangled_object.subscribe(node_name, event)
    for _ in range(5):
        await event.wait()
        value = getattr(tangled_object, node_name)
        print(f'{node_name}: {value}')
        event.clear()


async def main():
    # Create a foo and a bar object that contains the Element objects
    # that will build the graph.
    foo = Foo()
    bar = Bar(foo)

    # Prime the source nodes
    foo.source1 = 5.0
    foo.source2 = 3.0
    bar.source1 = 6.0

    # Create tasks to update the source nodes in foo and bar
    foo_source1 = asyncio.create_task(source_feeder(foo, 'source1'))
    foo_source2 = asyncio.create_task(source_feeder(foo, 'source2'))
    bar_source1 = asyncio.create_task(source_feeder(bar, 'source1'))

    # Create watcher tasks that listens for updates on foo_value and bar_value
    foo_watcher = asyncio.create_task(print_watcher(foo, 'foo_value'))
    bar_watcher = asyncio.create_task(print_watcher(bar, 'bar_value'))

    # Wait for the tasks to finish
    await asyncio.gather(foo_source1, foo_source2, bar_source1, foo_watcher, bar_watcher)


asyncio.run(main())

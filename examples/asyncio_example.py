""" Example of how to run tangle with asyncio.
"""
import asyncio
import random

from tangle import Tangled, TreeBuilder, BasicEvaluator

Tangled.set_handlers(TreeBuilder(), BasicEvaluator())


@Tangled.tangled_function
def average(a, b):
    """ Decorator ensures that this function can be used in a Tangled graph
    """
    return (a + b) / 2


class Foo(Tangled):
    source1 = TangledSource()
    source2 = TangledSource()

    foo_value = average(source1, source2)

    def __str__(self):
        return 'Foo<Instance>'


class Bar(Tangled):

    def __init__(self, foo):
        super().__init__()
        self._foo = foo

    @Tangled.tangled_map(Foo)
    def my_foo(self):
        """ The decorator ensures that Bar can find Element objects in the Foo
        class
        """
        return self._foo

    # Define a source on Bar
    source1 = TangledSource()

    # Defines a bar Element that references Elements on Foo. This is how
    # nodes can be dependant on nodes in other objects
    bar_value = (source1 + Foo.foo_value) / Foo.source1

    def __str__(self):
        return 'Bar<Instance>'


async def source_feeder(tangled_object, source_name):
    """This coroutine will update a source node with values at random intervals
    """
    for _ in range(4):
        await asyncio.sleep(random.uniform(0.5, 2))
        setattr(tangled_object, source_name, random.randint(-20, 20)/2.0)


async def print_watcher(tangled_object, node_name):
    """ A watcher of a node that prints when update happens.
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

    foo.source1 = 5.0
    foo.source2 = 3.0
    bar.source1 = 6.0

    foo_source1 = asyncio.create_task(source_feeder(foo, 'source1'))
    foo_source2 = asyncio.create_task(source_feeder(foo, 'source2'))
    bar_source1 = asyncio.create_task(source_feeder(bar, 'source1'))
    foo_watcher = asyncio.create_task(print_watcher(foo, 'foo_value'))
    bar_watcher = asyncio.create_task(print_watcher(bar, 'bar_value'))

    await asyncio.gather(foo_source1, foo_source2, bar_source1, foo_watcher, bar_watcher)


asyncio.run(main())

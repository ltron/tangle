""" Example of how to drive the directed graph of two objects using the curio"""
import random
import curio
import tangle
from tangle import basetreeprimitives, make_tangled_base

Tangled = make_tangled_base(basetreeprimitives)


@Tangled.tangled_function
async def do_stuff(a, b):
    """ Decorator ensures that this function can be used in a Tangled graph
    """ 
    return 10.0 * a / (4 * b)


class Foo(Tangled):

    # Setup two sources
    source1 = TangledSource()
    source2 = TangledSource()
    
    #  Setup a function node with the sources as input
    foo_value = do_stuff(source1, source2)


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
    bar_value = (source1 - Foo.foo_value) / Foo.source1


async def source_feeder(sources):
    """This coroutine will update a source node with values at random intervals
    """
    while True:
        chosen_source = random.choice(sources)
        await curio.sleep(random.uniform(0.5, 2))
        await chosen_source.set_value(random.uniform(-100,100))


async def print_watcher(node):
    """ A watcher of a node that prints when update happens.
    """
    node_name = node.name()
    update_event = curio.Event()
    node.register_for_notification(update_event)
    while True:
        await update_event.wait()
        value = await node.value()
        print(f'{node.name()}: {value}')
        update_event.clear()


async def main():
    # Create a foo and a bar object that contains the Element objects
    # that will build the graph.
    foo = Foo()
    bar = Bar(foo)

    # awaiting one of the Element attributes of an object will trigger
    # the building of that tree, all nodes this node is dependant on will
    # also be built. The source nodes will register with the source monitor
    calculation = await bar.bar_value

    # Starts the source feeder to feed random data into the source nodes
    all_sources = []
    all_sources.extend(foo.sources())
    all_sources.extend(bar.sources())
    for source in all_sources:
        await source.set_value(1.0)
    await curio.spawn(source_feeder(all_sources), daemon=True)

    # We can no setup a watcher that listens for updates on the node.
    # The print_watcher will print the final result from source node
    # updates
    watcher = await curio.spawn(print_watcher(calculation))

    await watcher.join()

curio.run(main())

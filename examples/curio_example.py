""" Example of how to drive the directed graph of two objects using the curio"""
import random
import curio
import tangle
from tangle import basetreeprimitives, make_tangled_base

async def source_feeder(source_node):
    """i This coroutine will update a source node with values at random intervals
    """
    while True:
        await curio.sleep(random.uniform(1,4))
        await source_node.set_value(random.uniform(-100,100))

source_queue = curio.Queue()

async def source_callback(obj, source_node):
    await source_queue.put(source_feeder(source_node))

async def source_monitor():
    while True:
        feeder = await source_queue.get()
        await curio.spawn(feeder, daemon=True)

Tangled = make_tangled_base(basetreeprimitives)

Tangled.register_source_monitor_callback(source_callback)

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

    # Starts the source monitor, this monitors the sources of data
    # and ensures that the source nodes are updated accordingly
    await curio.spawn(source_monitor(), daemon=True)

    # awaiting one of the Element attributes of an object will trigger
    # the building of that tree, all nodes this node is dependant on will
    # also be built. The source nodes will register with the source monitor
    calculation = await bar.bar_value

    # We can no setup a watcher that listens for updates on the node.
    # The print_watcher will print the final result from source node
    # updates
    watcher = await curio.spawn(print_watcher(calculation))

    await watcher.join()

curio.run(main())

import random
import curio
import tangle
from tangle import basetreeprimitives, make_tangled_base

async def source_feeder(source_node):
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
    return 10.0 * a / (4 * b)

class Foo(Tangled):

    source1 = TangledSource()

    source2 = TangledSource()

    foo_value = do_stuff(source1, source2)

class Bar(Tangled):

    def __init__(self, foo):
        super().__init__()
        self._foo = foo

    @Tangled.tangled_map(Foo)
    def my_foo(self):
        return self._foo

    source1 = TangledSource()

    bar_value = (source1 - Foo.foo_value) / Foo.source1

async def print_watcher(node):
    node_name = node.name()
    update_event = curio.Event()
    node.register_for_notification(update_event)
    while True:
        await update_event.wait()
        value = await node.value()
        print(f'{node.name()}: {value}')
        update_event.clear()

async def main():
    foo = Foo()
    bar = Bar(foo)

    await curio.spawn(source_monitor(), daemon=True)

    calculation = await bar.bar_value

    watcher = await curio.spawn(print_watcher(calculation))

    """source1 = await foo.source1
    source1.set_value(1.0)
    source2 = await foo.source2
    source2.set_value(2.0)
    source1 = await bar.source1
    source1.set_value(3.0)
    """
    await watcher.join()
    """
    print('bar_value dirty flag', bar.bar_value._dirty)
    print('Setting foo.source1 to 2.25')
    foo.source1.set_value(2.25)
    print('bar_value dirty flag after', bar.bar_value._dirty)
    print('New bar_value', bar.bar_value.value())
    """

curio.run(main())

import curio
import tangle
from tangle import basetreeprimitives, make_tangled_base

async def source_feeder(source_node):
    while true:
        await curio.sleep(random.random())
        source_node.set_value(random.random)

source_queue = curio.Queue()

def source_callback(obj, source_node):
    await source_queue.put(source_feeder(source_node))

async def source_monitor():
    while True:
        feeder = await source_queue.get()
        curio.spawn(feeder)

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
    update_event = node.subscribe()
    while True:
        await update_event
        value = node.value()
        print(value)

async def main():
    foo = Foo()
    bar = Bar(foo)

    print(bar.bar_value)

    print(foo._sourcenodes)
    print(bar._sourcenodes)
    """
    print('bar_value dirty flag', bar.bar_value._dirty)
    print('Setting foo.source1 to 2.25')
    foo.source1.set_value(2.25)
    print('bar_value dirty flag after', bar.bar_value._dirty)
    print('New bar_value', bar.bar_value.value())
    """
    #watcher1 = print_watcher(bar.foo_value)
    #watcher2 = print_watcher(foo.bar_value)

curio.run(main()

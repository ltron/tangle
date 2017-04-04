import asyncio
import tangle
from tangle import make_tree_primitives, make_tangled_base

def create_random_source():
    queue = asyncio.Queue()
    return queue

treeprimitives = make_tree_primitives(asyncio.Event)
Tangled = make_tangled_base(treeprimitives)

@Tangled.tangled_function
def do_stuff(a, b):
    return 10.0 * a / (4 * b)

class Foo(Tangled):

    source1 = TangledSource(create_random_source)

    source2 = TangledSource(create_random_source)

    foo_value = do_stuff(source1, source2)

class Bar(Tangled):

    def __init__(self, foo):
        super().__init__()
        self._foo = foo

    @Tangled.tangled_map(Foo)
    def my_foo(self):
        return self._foo
   
    source1 = TangledSource(create_random_source)

    bar_value = (source1 - Foo.foo_value) / Foo.source1

async def print_watcher(node):
    update_event = node.subscribe()
    while True:
        await update_event
        value = node.value()
        print(value)

foo = Foo()
bar = Bar(foo)

print('Bar calculation dict is empty:', bar.calculations)

# set some source values
foo.source1.set_value(2.0)
foo.source2.set_value(1.25)
bar.source1.set_value(0.5)

print('Calculate bar_value to', bar.bar_value.value())
print('Bar calculation dict is populated:', bar.calculations)

print('bar_value dirty flag', bar.bar_value._dirty)
print('Setting foo.source1 to 2.25')
foo.source1.set_value(2.25)
print('bar_value dirty flag after', bar.bar_value._dirty)
print('New bar_value', bar.bar_value.value())

#watcher1 = print_watcher(bar.foo_value)
#watcher2 = print_watcher(foo.bar_value)



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
        self._foo

    @Tangled.tangled_map(Foo)
    def my_foo(self):
        return self._foo
   
    source1 = TangledSource(create_random_source)

    bar_value = (source1 - Foo.foo_value) / Foo.source1

async def print_watcher(node):
    try:
        update_event = node.subscribe()
    except MissingEventException:
        update_event.update_event = asyncio.Event()
        update_event = node.subscribe()
    while True:
        await update_event
        value = node.value()
        print(value)

async def run():
    foo = Foo()
    bar = Bar(foo)

    watcher1 = print_watcher(bar.foo_value)
    watcher2 = print_watcher(foo.bar_value)



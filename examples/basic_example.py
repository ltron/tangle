import asyncio
from tangle import Tangled, tangle_source, tangled_function, tangled_mapping
from tangle import make_tree_primitives
import tangle

def create_random_source():
    queue = asyncio.Queue()
    return queue

@tangled_function
def do_stuff(a, b):
    return 10.0 * a / (4 * b)

treeprimitives = make_tree_primitives(asyncio.Event())
Tangled = make_tangled_base(treeprimitives)

class Foo(Tangled):

    source1 = tangle_source(create_random_source)

    source2 = tangle_source(create_random_source)

    foo_value = do_stuff(source1, source2)
    

class Bar(Tangled):

    def __init__(self, foo):
        self._foo

    @tangled_map(Foo)
    def my_foo(self):
        return self._foo
   
    source1 = tangle_source(create_random_source)

    bar_value = (source1 - Foo.node) / Foo.source1

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



import asyncio
from tangle import Tangled, tangle_source, PrintWatcher, tangled_function, tangled_map

def create_random_source():
    queue = asyncio.Queue()
    return queue

@tangled_function
def do_stuff(a, b):
    return 10.0 * a / (4 * b)

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
    update_even = node.subscribe()
    while True:
        await update_event
        value = node.value()
        print(value)

async def run():
    foo = Foo()
    bar = Bar(foo)

    watcher1 = print_watcher(bar.foo_value)
    watcher2 = print_watcher(foo.bar_value)






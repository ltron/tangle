import asyncio
from tangle import Tangled, tangle_source, print_watcher

def create_random_source():
    queue = asyncio.Queue()
    return queue 

class Foo(Tangled):

    source1 = tangle_source(create_random_source)

    source2 = tangle_source(create_random_source)

    node = source1 + source2

class Bar(Tangled):

    def __init__(self, foo):
        self._foo

    @mapping_to(Foo)
    def my_foo(self):
        return self._foo
   
    source1 = tangle_source(create_random_source)

    node = (source1 - Foo.node) / Foo.source1

foo = Foo()
bar = Bar(foo)

watcher = PrintWatcher()

watcher.watch(bar.node)
watcher.watch(foo.node)

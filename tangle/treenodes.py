""" Module containing the main node types of the data flow graph
"""
import asyncio

class BaseNode:
    """ Base class for all node types
    """

    def __init__(self):
        self._watchers = set()
        self._dependants = set()
        self._dirty = False
        self._value = None 

    def set_dirty(self):
        self._dirty = True
        for node in self._dependants:
            node.set_dirty()
        for watcher in self._watchers:
            # Create tasks that evaluates asynchronosly
            task = asyncio.ensure_future(watcher.evaluate())
    
    def add_dependant(self, other):
        self._dependants.add(other)


class FuncNode(BaseNode):
    """ Node that calls a function
    """
    def __init__(self, func, *args):
        super().__init__()
        self._func = func
        self._args = args
        for arg in args:
            arg.add_dependant(self)

    async def value(self):
        if not self._dirty:
            return self._value
        args = []
        for arg in self._args:
            value = await arg.value()
            args.append(value)
        self._value = self._func(*args)
        self._dirty = False
        return self._value

    def add_watcher(self, watcher):
        self._watchers.add(watcher)

class SourceNode(BaseNode):
    """ A node that is a source of values. The source object is queue like and should
    inplement an async get method. The source should be monitored by a coroutine
    that will also set the SourceNode to dirty.
    """
    def __init__(self, source):                
        super().__init__()
        self._source = source
    
    async def value(self):
        return self._value

async def source_node_monitor(node, source):
    try:
        print(source)
        while True:
            message = await source.get()
            if message:
                result = message.json()['price']
                message.ack()
                node._value = result
                node.set_dirty()
    except asyncio.CancelledError:
        # Finish silently on cancel
        pass

class PrintWatcher:
    def __init__(self, node):
        self.watched_node = node
        node.add_watcher(self)

    async def evaluate(self):
        value = await self.watched_node.value()
        print('Value:', value)




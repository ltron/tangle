""" Module containing the main node types of the data flow graph
"""
import asyncio

class BaseNode:
    """ Base class for all node types
    """

    def __init__(self):
        self._dependants = set()
        self._update_event = None
        self._cached_value = None
        self._dirty = True

    def notify_update(self):
        self._dirty = True
        for node in self._dependants:
            node.notify_update()
        if self.calculate_event:
            self.calculate_event.set()
    
    def add_dependant(self, other):
        self._dependants.add(other)

    def subscribe(self):
        if self._update_event is None:
            self._update_event = asyncio.Event()
        return self._update_event

class FuncNode(BaseNode):
    """ Node that calls a function
    """
    def __init__(self, func, *args):
        super().__init__()
        self._func = func
        self._args = args
        for arg in args:
            arg.add_dependant(self)

    def value(self):
        if not self._dirty:
            return self._cached_value
        args = []
        for arg in self._args:
            value = arg.value()
            args.append(value)
        self._cached_value = self._func(*args)
        self._dirty = False
        return self._cached_value

class SourceNode(BaseNode):
    """ A node that is a source of values. 
    The source object is queue like and should implement get
    """
    def __init__(self, source):                
        super().__init__()
        self.source = source
    
    def value(self):
        return self._cached_value

    def set_value(self, value):
        self._cached_value = value
        self.notify_update()

    async def monitor(self):
        try:
            print(source)
            while True:
                value = await self.source.get()
                self.set_value(value)
        except asyncio.CancelledError:
            # Finish silently on cancel
            pass

async def print_watcher(node):
    update_event = node.subscribe()
    while True:
        await update_event
        value = node.value()
        print(value)


class PrintWatcher:
    def __init__(self, node):
        self.watched_node = node
        node.add_watcher(self)

    async def evaluate(self):
        value = await self.watched_node.value()
        print('Value:', value)




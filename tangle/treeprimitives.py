""" Module containing example node objects that can be used by Element descriptors
to build a data flow graph
"""
import inspect
from types import SimpleNamespace

__all__ = ['basetreeprimitives']

class BaseNode:
    """ Base class for all node types
    """

    def __init__(self):
        self._dependants = set()
        self._update_events = set()
        self._cached_value = None
        self._dirty = True
        self._element = None
        self._initialised = False

    def __str__(self):
        if self._element:
            return '<Node %s>'%self._element.name
        else:
            return '<Node>'

    def __repr__(self):
        return self.__str__()

    async def notify_update(self):
        if self.is_initialised():
            # Only propagate update if this node (and its children)
            # are initialised 
            self._dirty = True
            for node in self._dependants:
                await node.notify_update()
            for event in self._update_events:
                await event.set()

    def add_dependant(self, other):
        self._dependants.add(other)

    def register_for_notification(self, event):
        self._update_events.add(event)

    @property
    def element(self):
        return self._element

    @element.setter
    def element(self, element):
        self._element = element

    def name(self):
        return self._element.name

class FunctionNode(BaseNode):
    """ A function node whose inputs are the child nodes.
    """
    def __init__(self, func, *args):
        super().__init__()
        self._func = func
        self.iscoroutinefunction = inspect.iscoroutinefunction(func)
        self._args = args
        for arg in args:
            arg.add_dependant(self)

    async def value(self):
        """ coroutine that calculates or returns a cached value
        """
        if not self._dirty:
            return self._cached_value
        args = []
        for arg in self._args:
            value = await arg.value()
            args.append(value)
        if self.iscoroutinefunction:
            # handle the case when the func is a coroutine
            self._cached_value = await self._func(*args)
        else:
            self._cached_value = self._func(*args)
        self._dirty = False
        return self._cached_value

    def is_initialised(self):
        if self._initialised:
            return True
        else:
            self._initialised = all([arg.is_initialised() for arg in self._args])
        return self._initialised

class ValueNode(BaseNode):
    """ A realised node that contians a value. Used as source nodes.
    """
    def __init__(self):
        super().__init__()
        self._initialised = False

    async def value(self):
        return self._cached_value

    def is_initialised(self):
        return self._initialised

    async def set_value(self, value):
        self._initialised = True
        self._cached_value = value
        await self.notify_update()

basetreeprimitives = SimpleNamespace(FunctionNode = FunctionNode,
                                 ValueNode = ValueNode)



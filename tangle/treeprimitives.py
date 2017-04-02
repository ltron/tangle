""" Module containing the main node types of the data flow graph
"""
from types import SimpleNamespace

__all__ = ['make_tree_primitives']

def make_tree_primitives(Event):

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
                self._update_event = Event()
            return self._update_event

    class FunctionNode(BaseNode):
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

    class ValueNode(BaseNode):
        """ A node that is a value. 
        """
        def __init__(self, source):                
            super().__init__()
            self.source = source
        
        def value(self):
            return self._cached_value

        def set_value(self, value):
            self._cached_value = value
            self.notify_update()

    return SimpleNamespace(FunctionNode = FunctionNode,
                            ValueNode = ValueNode)



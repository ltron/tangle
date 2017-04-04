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
            self._element = None

        def __str__(self):
            if self._element:
                return '<Node %s>'%self._element.name
            else:
                return '<Node>'

        def __repr__(self):
            return self.__str__()

        def notify_update(self):
            self._dirty = True
            for node in self._dependants:
                node.notify_update()
            if self._update_event:
                self._update_event.set()
        
        def add_dependant(self, other):
            self._dependants.add(other)

        def subscribe(self):
            if self._update_event is None:
                self._update_event = Event()
            return self._update_event
        
        @property
        def element(self):
            return self._element

        @element.setter
        def element(self, element):
            self._element = element

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
        def __init__(self):                
            super().__init__()
        
        def value(self):
            return self._cached_value

        def set_value(self, value):
            self._cached_value = value
            self.notify_update()

    return SimpleNamespace(FunctionNode = FunctionNode,
                            ValueNode = ValueNode)



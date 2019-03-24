""" Module containing example node objects that can be used by Element descriptors
to build a data flow graph
"""

from weakref import WeakSet

__all__ = ['FunctionNode', 'ContainerNode', 'ValueNode']


class BaseNode:
    """ Base class for all node types
    """

    __slots__ = ['blueprint',
                 'instance',
                 '_dependants',
                 '_update_events',
                 '_cached_value',
                 'dirty']

    def __init__(self, blueprint, instance):
        self.blueprint = blueprint
        self.instance = instance
        self._dependants = set()
        self._update_events = WeakSet()
        self._cached_value = None
        self.dirty = True

    def __str__(self):
        if not self.blueprint.is_anonymous():
            owner_class = self.blueprint.owner_class.__name__
            return '<Node(%s.%s)>'%(owner_class,
                                    self.blueprint.name)
        else:
            return '<Node>'

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        if self.blueprint.is_anonymous():
            return '<AnonymousNode>'
        return self.blueprint.name

    def notify_update(self):
        for node in self._dependants:
            node.dirty = True
            node.notify_update()
        for event in self._update_events:
            event.set()

    def add_as_dependant(self, other):
        self._dependants.add(other)

    def register_event(self, event):
        """ Registers an event that gets set when this node
        is set to dirty.

        :param event:
        :return:
        """
        self._update_events.add(event)

    def value(self):
        """ calculates or returns a cached value
        """
        if self.dirty:
            raise Exception('Todo Strange exception rename')
        return self._cached_value


class FunctionNode(BaseNode):
    """ A function node whose inputs are the child nodes.
    """

    __slots__ = ['_func',
                 'arg_nodes']

    is_value_node = False

    def __init__(self, blueprint, instance, *arg_nodes):
        super().__init__(blueprint, instance)
        self._func = blueprint.func
        self.arg_nodes = arg_nodes
        for arg_node in arg_nodes:
            arg_node.add_as_dependant(self)

    def calculate(self):
        if not self.dirty:
            return
        args = []
        for arg_node in self.arg_nodes:
            args.append(arg_node.value())
        self._cached_value = self._func(*args)
        self.dirty = False


class ContainerNode(FunctionNode):

    def calculate(self):
        if not self.dirty:
            return
        args = []
        for arg_node in self.arg_nodes:
            args.append(arg_node.value())
        self._cached_value = self._func(args)
        self.dirty = False


class ValueNode(BaseNode):
    """ A realised node that contains a value. Used as source nodes.
    """

    __slots__ = []

    is_value_node = True

    def __init__(self, blueprint, instance):
        super().__init__(blueprint, instance)

    def set_value(self, value):
        if self._cached_value == value:
            return
        self._cached_value = value
        self.notify_update()
        self.dirty = False

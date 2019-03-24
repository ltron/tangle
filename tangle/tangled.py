from weakref import WeakSet
from functools import wraps

from .blueprints import NodeBlueprint, FuncBlueprint, TangledSource, TangledSelf, TangledList
from .exceptions import NodeError

__all__ = ['Tangled',
           'tangled_function',
           'tangled_link']


class TangleMeta(type):

    @classmethod
    def __prepare__(mcs, name, bases):
        """ Setting up class attributes so they are available when the a
        tangled class body is executed.
        """
        namespace = {'TangledSource': TangledSource,
                'self': TangledSelf(),
                'tlist': TangledList
                }
        for superclass in bases:
            for attr_name, attr in superclass.__dict__.items():
                if isinstance(attr, NodeBlueprint):
                    namespace[attr_name] = attr
        return namespace

    def __new__(meta, name, bases, namespace):
        namespace['tangled_maps'] = {}
        return super().__new__(meta, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        """ Setup various class attributes that need to be available for all
        Tangled sub classes
        """
        for name, attr in namespace.items():
            if name in ('self', 'TangledSource', 'tlist'):
                continue
            if hasattr(attr, 'mapping_for'):
                # sets up a map between classes, so that it's possible
                # to refer to Element instances with other owner classes
                namespace['tangled_maps'][attr.mapping_for] = attr
        super().__init__(name, bases, namespace)


class Tangled(metaclass=TangleMeta):
    """ Base class for tangled behaviour.
    """

    builder = None
    evaluator = None

    def __init__(self):
        self.nodes = {}
        self._dependants = set()
        self._update_events = WeakSet()

    @classmethod
    def set_handlers(cls, builder, evaluator):
        cls.builder = builder
        cls.evaluator = evaluator

    def subscribe(self, node_name, event):
        try:
            # Initialise tree if required
            getattr(self, node_name)
            node = self.nodes[node_name]
        except KeyError:
            raise NodeError(f'No node {node_name} to subscribe to.')
        node.register_event(event)

    def notify_update(self):
        for node in self._dependants:
            node.dirty = True
            node.notify_update()
        for event in self._update_events:
            event.set()

    def add_as_dependant(self, other):
        self._dependants.add(other)

    # TODO Treating Tangled instances as value nodes should probably
    # be more explicit

    is_value_node = True

    def value(self):
        """ Treats a tangled object as a value node so we can have it in the graph
        specifically when calling a method.
        """
        return self


def tangled_function(func):
    """ Decorator to create a tangled function element
    """
    @wraps(func)
    def wrapper(*args):
        return FuncBlueprint(func, *args)
    return wrapper


def tangled_link(other):
    """ Decorator that registers the method to be a mapping to
    the class other
    """
    def register(func):
        func.mapping_for = other
        return func
    return register

"""
def artdeco(hej):
    def wrap(f):
        def wrapped_f(*args, **kwds):
            return f(*args, **kwds)
        return wrapped_f
    return wrap
"""


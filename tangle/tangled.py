from functools import wraps
from weakref import WeakSet

from .blueprints import NodeBlueprint, TangledSource, TangledSelf, LinkBlueprint, tmap
from .exceptions import NodeError

__all__ = ['Tangled']

class TangleMeta(type):

    @classmethod
    def __prepare__(mcs, name, bases):
        """ Setting up class attributes so they are available when the a
        tangled class body is executed.
        """
        return {'TangledSource': TangledSource,
                'self': TangledSelf(),
                'tmap': tmap
                }

    def __new__(meta, name, bases, namespace):
        namespace['tangled_maps'] = {}
        return super().__new__(meta, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        """ Setup various class attributes that need to be available for all
        Tangled sub classes
        """
        for name, attr in namespace.items():
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
        self._dependents = WeakSet()

    @classmethod
    def set_handlers(cls, builder, evaluator):
        cls.builder = builder
        cls.evaluator = evaluator

    @staticmethod
    def tangled_function(func):
        """ Decorator to create a tangled function element
        """
        @wraps(func)
        def wrapper(*args):
            return NodeBlueprint(func, *args)
        return wrapper

    @staticmethod
    def link(method):
        """ Decorator that registers the method to be a mapping to
        the class other
        """
        _map = TangledLink(method)
        return _map

    def subscribe(self, node_name, event):
        try:
            # Initialise tree if required
            getattr(self, node_name)
            node = self.nodes[node_name]
        except KeyError:
            raise NodeError(f'No node {node_name} to subscribe to.')
        node.register_event(event)

    @classmethod
    def get_blueprint(cls, name):
        return cls.__dict__[name]

class TangledLink(object):
    def __init__(self, method):
        self.method = method

    def __call__(self, instance):
        return self.method(instance)

    def __getattr__(self, blueprint_name):
        """ Tangled map "method" should look through to the underlying class 
        for blueprints
        """
        return LinkBlueprint(self.method, blueprint_name)

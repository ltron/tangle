from functools import wraps

from .blueprints import NodeBlueprint, TangledSource, TangledSelf
from .builder import TreeBuilder
from .evaluator import Evaluator
from .mappers import TangledMapper

__all__ = ['Tangled']


class TangleMeta(type):

    @classmethod
    def __prepare__(mcs, name, bases):
        """ Setting up class attributes so they are available when the a
        tangled class body is executed.
        """
        return {'TangledSource': TangledSource,
                'self': TangledSelf()
                }

    def __new__(meta, name, bases, namespace):
        namespace['tangled_maps'] = {}
        namespace['builder'] = TreeBuilder()
        namespace['evaluator'] = Evaluator()
        namespace['mapper'] = TangledMapper()
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

    def __init__(self):
        self.nodes = {}

    @staticmethod
    def tangled_function(func):
        """ Decorator to create a tangled function element
        """
        @wraps(func)
        def wrapper(*args):
            return NodeBlueprint(func, *args)
        return wrapper

    @staticmethod
    def tangled_map(other):
        """ Decorator that registers the method to be a mapping to
        the class other
        """
        def register(func):
            func.mapping_for = other
            return func
        return register

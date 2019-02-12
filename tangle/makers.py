""" Classes for building the graphs
"""
import operator
from functools import wraps
from .treeprimitives import basetreeprimitives

__all__ = ['Tangled']


class NodeMaker(object):
    """ Descriptor used as part of the blueprint for building the instance graph.
    """

    def __init__(self, func, *args):
        """
        func - callable that will be applied to the results of the input nodes
        args - input Element descriptors, these will provide the input to func in
                the realised node.
        """
        self.func = func
        self.args = args
        self.name = None
        self.owner_class = None

    def __str__(self):
        class_name  = self.__class__.__name__
        return f'<{class_name} "{self.name}">'

    # this is the new initializer:
    def __set_name__(self, owner_class, name):
        self.owner_class = owner_class
        self.name = name


    def is_anonymous(self):
        """ Anonymous elements do not have an owner, in that case
        this returns None
        """
        return self.owner_class is None

    def node_for_other_class(self, instance):
        return not self.is_anonymous() and not isinstance(instance, self.owner_class)

    def build_node(self, instance, arg_nodes):
        arg_nodes = [arg.get_or_build_node(instance) for arg in self.args]
        return instance.treeprimitives.FunctionNode(self.func, *arg_nodes)

    def get_or_build_node(self, instance):
        """ Build or return cached valuation graph.

        instance - this is the class instance that this node is tied to
        """

        # Todo add builder class to handle recursion depth?!!

        if self.node_for_other_class(instance):
            instance = instance.get_mapped_object(self.owner_class)
        # check if calculation already exists
        calculation = instance._calculations.get(self.name, None)
        if calculation:
            return calculation

        arg_nodes = [arg.build_tree(instance) for arg in self.args]
        tree_node = self.build_node(instance, arg_nodes)
        tree_node.element = self
        if not self.is_anonymous():
            instance._calculations[self.name] = tree_node
        return tree_node

    def __get__(self, instance, cls):
        """ descriptor protocol implementation
        """
        if instance is not None:
            # If accessed from an instance, build or return cached tree
            calculation = self.get_or_build_node(instance)
            return calculation
        elif cls:
            # If we access from a class then return self so it can be used to
            # build blueprint graph
            return self

    # Magic methods create new NodeMakers objects for all standard operations
    # These elements won't have a name and is thus anonymous
    def __add__(self, other):
        return NodeMaker(operator.add, self, other)

    def __matmul__(self, other):
        return NodeMaker(operator.matmul, self, other)

    def __mul__(self, other):
        return NodeMaker(operator.mul, self, other)

    def __sub__(self, other):
        return NodeMaker(operator.sub, self, other)

    def __truediv__(self, other):
        return NodeMaker(operator.truediv, self, other)


class TangledSource(NodeMaker):

    def __init__(self):
        self.name = None
        self.owner_class = None
        self.args = ()

    def build_node(self, instance, args):
        return instance.treeprimitives.ValueNode()

    def __set__(self, instance, value):
        node = self.get_or_build_node(instance)
        node.set_value(value)


class MethodCallMaker(NodeMaker):
    """ Element to allow graph building in an element type way
    """
    def __init__(self, method_name):
        self.method_name = method_name
        super().__init__(None)

    def build_node(self, obj, args):
        method = getattr(obj, element.method_name)
        node = treeprimitives.FunctionNode(method, obj, args)
        return node


class TangledSelf(NodeMaker):
    """ object that is a proxy for the class itself. To be able
    to build the graph from a method call.
    """

    def __init__(self):
        super().__init__(None)

    def __getattr__(self, method_name):
        return MethodCallMaker(method_name)


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
        self._calculations = {}

    _treeprimitives = basetreeprimitives

    @property
    def treeprimitives(self):
        return self._treeprimitives

    def get_mapped_object(self, other_class):
        try:
            return self.tangled_maps[other_class](self)
        except:
            my_class_name = self.__class__.__name__
            other_class_name = other_class.__name__
            msg = f'No tangled map between {my_class_name} and {other_class_name}'
            raise MappingError(msg)

    @staticmethod
    def tangled_function(func):
        """ Decorator to create a tangled function element
        """
        @wraps(func)
        def wrapper(*args):
            return NodeMaker(func, *args)
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


class TangledMapper(object):
    """ Class that implements relations between instances of one class to the other.
    """

    def __getitem__(self, item):
        raise NotImplementedError()

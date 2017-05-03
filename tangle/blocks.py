import operator
from functools import partial, wraps
from collections import defaultdict

__all__ = ['make_tangled_base']

class MappingError(Exception):
    pass

def make_tangled_base(treeprimitives):
    """ Creates the Tangled base class. If a class inherits from this it will be
    able be part of a tangled graph structure

    treeprimitives - a name space with the node primitives which will be part
                     of the instance graphs.
    """

    class Element(object):
        def __init__(self, func, *args):
            self.func = func
            self.args = args
            self.name = None
            self.owner = None

        def __str__(self):
            return '<Element %s>'%self.name

        def __repr__(self):
            return '<Element %s>'%self.name

        # class operators
        def __add__(self, other):
            return Element(operator.add, self, other)

        def __matmul__(self, other):
            return Element(operator.matmul, self, other)

        def __mul__(self, other):
            return Element(operator.mul, self, other)

        def __sub__(self, other):
            return Element(operator.sub, self, other)

        def __truediv__(self, other):
            return Element(operator.truediv, self, other)

        def is_anonymous(self):
            """ Anonymous functions do not have a owner.
            """
            return self.owner is None

        def build_node(self, obj, arg_nodes):
            tree_node = treeprimitives.FunctionNode(self.func, *arg_nodes)
            return tree_node

        def build_tree(self, obj):
            """ Build or return cached valuation graph
            """
            if not self.is_anonymous() and not isinstance(obj, self.owner):
                # Element belongs to another class than the obj class
                obj = obj.get_mapped_object(self.owner)
            calculation = obj.calculations.get(self.name, None)
            if calculation:
                return calculation

            arg_nodes = [arg.build_tree(obj) for arg in self.args]
            tree_node = self.build_node(obj, arg_nodes)
            tree_node.element = self
            if not self.is_anonymous():
                obj.calculations[self.name] = tree_node
            return tree_node

        def __get__(self, instance, cls):
            if instance is not None:
                # If we have a class instance we build the valuation
                # graph
                calculation = self.build_tree(instance)
                return calculation
            elif cls:
                # if no instance then the was accessed on a class in 
                # that case we want to return the Element descritor
                # so it can be used to build a graph
                return self


    class TangledSource(Element):
        """ Element that represents a source of data.
        """
        def __init__(self, source_factory):
            # source_Factory is a callable that returns e.g. an async queue
            # the queue will be the source of the data
            super().__init__(None)

        def build_node(element, obj, args):
            return treeprimitives.ValueNode()

    class MethodElement(Element):
        """ Element to allow method type building of the element graph
        """
        def __init__(self, method_name):
            self.method_name = method_name
            super().__init__(None)

        def build_node(self, obj, args):
            method = getattr(obj, element.method_name)
            node = treeprimitives.FunctionNode(method, obj, args)

    class TangledSelf(Element):
        """ object that is a proxy for the class itself. To be able
        to build the graph from a method call.
        """

        def __init__(self):
            super().__init__(None)

        def __getattr__(self, method_name):
            return MethodElement(method_name)

    class TangleMeta(type):
        """ Go through all the Element descriptors and set the attribute
        name on them. So we can identify the calculation nodes by name
        """

        def __prepare__(names, bases, **kwds):
            return {'TangledSource': TangledSource}

        def __new__(meta, name, bases, namespace):
            namespace['tangled_maps'] = {}
            return type.__new__(meta, name, bases, namespace)

        def __init__(cls, name, bases, namespace):
            super().__init__(name, bases, namespace)
            for name, attr in namespace.items():
                if isinstance(attr, Element):
                    attr.name = name
                    attr.owner = cls
                elif hasattr(attr, 'mapping_for'):
                    namespace['tangled_maps'][attr.mapping_for] =  attr


    class Tangled(metaclass=TangleMeta):
        """ Base class for tangled behaviour.
        """

        self = TangledSelf()

        def __init__(self):
            self.calculations = {}
            self.sources = set()

        def get_mapped_object(self, other_class):
            try:
                return self.tangled_maps[other_class](self)
            except:
                my_class_name = self.__class__.__name__
                other_class_name = other_class.__name__
                msg = 'No tangled map between {} and {}'.format(my_class_name,
                                                            other_class.__name__)
                raise MappingError(msg)

        @staticmethod
        def tangled_function(func):
            """ Decorator to create a tangled function element
            """
            @wraps(func)
            def wrapper(*args):
                return Element(func, *args)
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



    return Tangled



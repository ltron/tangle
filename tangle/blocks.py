""" This module provides the Element descriptor object. These are used as blueprints to
build a graph. It also provides the Tangled class. A class that inherits from Tangled
will be able to be part of the graph.
"""
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
                     of the instance graphs. These are the actual node objects.
    """

    class Element(object):
        """ Desciptor used as part of the blueprint for building the instance graph.
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
            self.owner = None

        def __str__(self):
            return '<Element %s>'%self.name

        def __repr__(self):
            return '<Element %s>'%self.name
        
        # Magic methods create new Element objects for all standard operations 
        # These elements won't have a new and is thus anonymous
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
            """ Anonymous elements do not have an owner, in that case
            this returns None
            """
            return self.owner is None

        async def build_node(self, obj, arg_nodes):
            """ Build an actual graph node
            """
            tree_node = treeprimitives.FunctionNode(self.func, *arg_nodes)
            return tree_node

        async def build_tree(self, obj):
            """ Build or return cached valuation graph.

            obj - this is the class instance that this node is tied to
            """
            if not self.is_anonymous() and not isinstance(obj, self.owner):
                # Element belongs to another class than the obj class
                obj = obj.get_mapped_object(self.owner)
            # check if calculation already exists
            calculation = obj._calculations.get(self.name, None)
            if calculation:
                return calculation

            arg_nodes = [await arg.build_tree(obj) for arg in self.args]
            tree_node = await self.build_node(obj, arg_nodes)
            tree_node.element = self
            if not self.is_anonymous():
                obj._calculations[self.name] = tree_node
            return tree_node

        def __get__(self, instance, cls):
            """ descriptor protocol implementation
            """
            if instance is not None:
                # If we have a class instance we build the valuation
                # graph. This returns a coroutine that has to
                # be awaited
                calculation = self.build_tree(instance)
                return calculation
            elif cls:
                # if no instance then the was accessed on a class in 
                # that case we want to return the Element descriptor
                # so it can be used to build a graph
                return self


    class TangledSource(Element):
        """ Element that represents a source of data.
        """
        def __init__(self):
            super().__init__(None)

        async def build_node(self, obj, args):
            tree_node = treeprimitives.ValueNode()
            await obj.register_source(self.name, tree_node)
            return tree_node

    class MethodElement(Element):
        """ Element to allow graph building in an element type way
        """
        def __init__(self, method_name):
            self.method_name = method_name
            super().__init__(None)

        async def build_node(self, obj, args):
            method = getattr(obj, element.method_name)
            node = treeprimitives.FunctionNode(method, obj, args)
            return node

    class TangledSelf(Element):
        """ object that is a proxy for the class itself. To be able
        to build the graph from a method call.
        """

        def __init__(self):
            super().__init__(None)

        def __getattr__(self, method_name):
            return MethodElement(method_name)

    class TangleMeta(type):
        """ Goes through all the Element descriptors and set the attribute
        name on them. So we can identify the calculation nodes by name and
        cache them by the same name
        """

        def __prepare__(names, bases, **kwds):
            return {'TangledSource': TangledSource,
                    'self': TangledSelf()}

        def __new__(meta, name, bases, namespace):
            namespace['tangled_maps'] = {}
            return super().__new__(meta, name, bases, namespace)

        def __init__(cls, name, bases, namespace):
            for name, attr in namespace.items():
                if isinstance(attr, Element):
                    # Sets name and owner on a Element object
                    attr.name = name
                    attr.owner = cls
                elif hasattr(attr, 'mapping_for'):
                    # sets up a map between classes, so that it's possible
                    # to refer to Element instances with other owner classes
                    namespace['tangled_maps'][attr.mapping_for] =  attr
            super().__init__(name, bases, namespace)

    class Tangled(metaclass=TangleMeta):
        """ Base class for tangled behaviour.
        """

        source_monitor_callbacks = set()

        def __init__(self):
            self._calculations = {}
            self._sources = {}

        def get_mapped_object(self, other_class):
            try:
                return self.tangled_maps[other_class](self)
            except:
                my_class_name = self.__class__.__name__
                other_class_name = other_class.__name__
                msg = 'No tangled map between {} and {}'.format(my_class_name,
                                                            other_class.__name__)
                raise MappingError(msg)

        async def register_source(self, name, tree_node):
            """ Called when a source node is created. Calls all registered
            source monitor callbacks. These typically ensures that the source
            node recieves updates. These updates drive the graph. 
            """
            self._sources[name] = tree_node

        def sources(self):
            return self._sources.values()

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



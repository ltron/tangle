""" Classes for building the graphs
"""
from .treeprimitives import basetreeprimitives

__all__ = ['Tangled']


class NodeMaker(object):
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

    def get_or_build_node(self, instance):
        return instance.treeprimitives.FunctionNode(self.func, *arg_nodes)

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


class TangledSource(NodeMaker):
    pass


class MethodCallMaker(NodeMaker):
    """ Element to allow graph building in an element type way
    """
    def __init__(self, method_name):
        self.method_name = method_name
        super().__init__(None)

    async def build_node(self, obj, args):
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

    def __prepare__(name, bases, **kwds):
        print('Preparing', name)
        return {'TangledSource': TangledSource,
                'self': TangledSelf()
                }

    def __new__(meta, name, bases, namespace):
        return super().__new__(meta, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        print('Init', name)
        print(namespace)
        namespace['_calculations'] = {}
        namespace['_sources'] = {}
        namespace['tangled_maps'] = {}
        for name, attr in namespace.items():
            if isinstance(attr, NodeMaker):
                # Sets name and owner on a NodeMaker instance
                attr.name = name
                attr.owner = cls
            elif hasattr(attr, 'mapping_for'):
                # sets up a map between classes, so that it's possible
                # to refer to Element instances with other owner classes
                namespace['tangled_maps'][attr.mapping_for] =  attr
        super().__init__(name, bases, namespace)
        print(namespace)

class Tangled(metaclass=TangleMeta):
    """ Base class for tangled behaviour.
    """

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

class TangledMapper(object):
    """ Class that implements relations between instances of one class to the other.
    """

    def __getitem__(self, item):
        raise NotImplementedError()

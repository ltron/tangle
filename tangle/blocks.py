import operator
from functools import partial, wraps
from collections import defaultdict
from .treeprimitives import SourceNode, FuncNode, MethodNode, PrintWatcher 
from .treeprimitives import source_node_monitor



class MappingError(Exception):
    pass

def tangled_function(func):
    """ Decorator to create a tangled function element
    """
    @wraps(func)
    def wrapper(*args):
        return Element(func, *args)
    return wrapper

def tangled_mapping(other):
    """ Decorator that registers the method to be a mapping to
    the class other
    """
    def register(func):
        func.mapping_for = other
        return func
    return register 

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
            self.is_method_call = False
            self.is_source = False

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

        @staticmethod
        def build_tree(obj, element):
            """ Build or return cached valuation graph
            """
            if not isinstance(obj, element.owner):
                obj = obj.get_mapped_object(element.owner)

            calculation = obj.calculations.get(element.name, None)
            if calculation:
                return calculation
            args = [build_tree(obj, arg) for arg in element.args]
            if element.is_source:
                # Source Element should have func taking instance
                # as input and returns a queue with async get method
                source_node = treeprimitives.ValueNode(element.source_factory(obj))
            elif element.is_method_call:
                # how to call a method?
                method = getattr(obj, element.method_name)
                treeprimitives.FunctionNode(method, obj)
            return treeprimitives.FunctionNode(element.func, *args)

        # other methods
        def __get__(self, instance, cls):
            if instance is not None:
                # If we have a class instance we build the valuation
                # graph
                calculation = self.build_tree(instance, self) 
                return calculation
            elif cls:
                # if no instance then the was accessed on a class in 
                # that case we want to return the Element descritor
                # so it can be used to build a graph
                return self


    class SourceElement(Element):
        """ Element that represents a source of data. 
        """
        def __init__(self, source_factory):
            # source_Factory is a callable that returns e.g. an async queue
            # the queue will be the source of the data
            super().__init__(None)
            self.source_factory = source_factory
            self.is_source = True

    class TangledSelf(Element):
        """ object that is a proxy for the class itself. To be able
        to build the graph from a method call.
        """
        def __getattr__(self, method_name):
            return MethodName(method_name)

    class MethodElement(Element):
        """ Element to allow method type building of the element graph
        """
        def __init__(self, method_name):
            self.method_name = method_name
            super().__init__(None)

    class TangleMeta(type):
        """ Go through all the Element descriptors and set the attribute
        name on them. So we can identify the calculation nodes by name
        """

        calculations = defaultdict(dict)

        def __new__(meta, name, bases, namespace):
            namespace['mappings'] = {}
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

        def get_mapped_object(self, other_clas):
            try:
                return self.tangled_map[other_class](self)
            except:
                my_class_name = self.__class__.__name__
                other_class_name = cls.__name__
                msg = 'No tangled map between {} and {}'.format(my_class_name,
                                                            cls.__name__)
                raise MappingError(msg)

    return Tangled



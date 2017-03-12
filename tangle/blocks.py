import operator
from functools import partial, wraps
from collections import defaultdict
from .treenodes import SourceNode, FuncNode, MethodNode, PrintWatcher 
from .treenodes import source_node_monitor


class Element:
    def __init__(self, func, *args):
        self.func = func
        self.args = args
        self.name = None
        self.owner = None
        self.is_object = True
        self.is_source = False

    def __add__(self, other):
        return Element(operator.add, self, other)

    def __sub__(self, other):
        return Element(operator.sub, self, other)

    def __mul__(self, other):
        return Element(operator.mul, self, other)

    def __truediv__(self, other):
        return Element(operator.truediv, self, other)

    def __get__(self, instance, cls):
        if instance is not None:
            calculation = build_calculation(instance, self) 
            return calculation
        elif cls:
            return self

class SourceElement(Element):
    """ Element that represents a source of data. 
    """
    def __init__(self, source_factory):
        # source_Factory is a callable that returns a async queue
        # the queue will be the source of the data
        super().__init__(None)
        self.source_factory = source_factory
        self.is_source = True

class MethodElement(Element):
    def __init__(self, method_name):
        self.method_name = method_name
        super().__init__(None)

class TangledSelf(object):
    def __getattr__(self, method_name):
        return MethodName(method_name)

def build_calculation(obj, element):
    print(element.name, element.owner)
    if not isinstance(obj, element.owner):
        obj = obj.get_mapped_object(element.owner)

    calculation = obj.calculations.get(element.name, None)
    if calculation:
        return calculation
    args = [build_calculation(obj, arg) for arg in element.args]
    if element.is_source:
        # Source Element should have func taking instance
        # as input and returns a queue with async get method
        return SourceNode(element.source_factory(obj))
    elif element.is_object:
        # how to call a method?
        method_name = element.method_name
        return MethodNode(obj, element.method_name)
    return FuncNode(element.func, *args)

def dag_node(func):
    @wraps(func)
    def wrapper(*args):
        return Element(func, *args)
    return wrapper


class TangleMeta(type):
    """ Go through all the Element descriptors and set the attribute
    name on them.
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
                namespace['mappings'][attr.mapping_for] =  attr

class MappingError(Exception):
    pass

class Tangled(metaclass=TangleMeta):

    def __init__(self):
        self.calculations = {}

    def get_mapped_object(self, cls):
        try:
            return self.mappings[cls](self)
        except:
            my_class_name = self.__class__.__name__
            other_class_name = cls.__name__
            msg = 'No mapping between {} and {}'.format(my_class_name,
                                                        cls.__name__)

            raise MappingError(msg)
                    
def register_as_mapping(other):
    def do_registring(func):
        func.mapping_for = other
        return func
    return do_registring

def get_source():
    return Element(None)


"""
class A(DagBase):

    def __init__(self, name):
        super().__init__()
        self.name = name

    source1 = get_source()

    source2 = get_source()

    value_a = source1 + source2

class B(DagBase):

    def __init__(self, name, a):
        super().__init__()
        self.name = name
        self.a = a

    @register_as_mapping(A)
    def get_a(self):
        return self.a
   
    source1 = get_source()

    value_b = A.value_a + A.source1

a = A('a')
b = B('b', a)

calculation = b.value_b
"""

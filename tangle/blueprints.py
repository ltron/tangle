""" Classes for building the graphs
"""
import operator

__all__ = ['NodeBlueprint', 'TangledSelf', 'TangledSource', 'MethodCallBlueprint', 'tmap']


class NodeBlueprint(object):
    """ Descriptor used as part of the blueprint for building the instance graph.
    """

    def __init__(self, func, *blueprint_args):
        """
        func - callable that will be applied to the results of the input nodes
        args - input Element descriptors, these will provide the input to func in
                the realised node.
        """
        self.func = func
        self.blueprint_args = blueprint_args
        self.name = id(self)
        self.owner_class = None

    def __str__(self):
        class_name  = self.__class__.__name__
        return f'<{class_name} "{self.name}">'

    def __repr__(self):
        return self.__str__()

    def __set_name__(self, owner_class, name):
        self.owner_class = owner_class
        self.name = name

    @property
    def arg_count(self):
        return len(self.blueprint_args)

    @property
    def is_value_node(self):
        return False

    def is_anonymous(self):
        """ Anonymous elements do not have an owner, in that case
        this returns None
        """
        return self.owner_class is None

    def node_for_other_class(self, instance):
        return not self.is_anonymous() and not isinstance(instance, self.owner_class)

    def get_or_build_node(self, instance):
        tree_node = instance.builder.build(instance, self)
        return tree_node

    def __get__(self, instance, cls):
        """ descriptor protocol implementation
        """
        if instance is not None:
            # If accessed from an instance, build or return cached tree
            node = self.get_or_build_node(instance)
            instance.evaluator.evaluate(node)
            result = node.value()
            return result
        elif cls:
            # If we access from a class then return self so it can be used to
            # build the blueprint graph
            return self

    # Magic methods create new NodeMakers objects for all standard operations
    # These elements won't have a name and is thus anonymous
    def __add__(self, other):
        return NodeBlueprint(operator.add, self, other)

    def __matmul__(self, other):
        return NodeBlueprint(operator.matmul, self, other)

    def __mul__(self, other):
        return NodeBlueprint(operator.mul, self, other)

    def __sub__(self, other):
        return NodeBlueprint(operator.sub, self, other)

    def __truediv__(self, other):
        return NodeBlueprint(operator.truediv, self, other)


class TangledSource(NodeBlueprint):

    def __init__(self):
        self.name = None
        self.owner_class = None
        self.args = ()

    @property
    def arg_count(self):
        return 0

    @property
    def is_value_node(self):
        return True

    def __set__(self, instance, value):
        node = self.get_or_build_node(instance)
        node.set_value(value)


class MethodCallBlueprint(NodeBlueprint):
    """ Element to allow graph building in an element type way
    """
    def __init__(self, method_name):
        self.method_name = method_name
        super().__init__(None)

    def build_node(self, obj, args):
        method = getattr(obj, element.method_name)
        node = treeprimitives.FunctionNode(method, obj, args)
        return node


class TangledSelf(NodeBlueprint):
    """ object that is a proxy for the class itself. To be able
    to build the graph from a method call.
    """

    def __init__(self):
        super().__init__(None)

    def __getattr__(self, method_name):
        return MethodCallBlueprint(method_name)

def _tmap(blueprint_name):
    def wrap(collection):
        blueprint_name
        1+1
    return wrap

def tmap(method_call, blueprint_name):
    return NodeBlueprint(_tmap(blueprint_name), method_call)

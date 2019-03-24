""" Banan
"""
import logging
from collections import deque

from .bricks import FunctionNode, ContainerNode, ValueNode
from .blueprints import NodeBlueprint
from .mappers import TangledMapper

__all__ = ['TreeBuilder']

log = logging.getLogger(__name__)


class TreeBuilder(object):

    def __init__(self,
                 function_node_factory=FunctionNode,
                 value_node_factory=ValueNode,
                 container_node_factory=ContainerNode,
                 instance_mapper=None
                 ):
        self.function_node_factory = function_node_factory
        self.container_node_factory = container_node_factory
        self.value_node_factory = value_node_factory
        self.mapper = instance_mapper if instance_mapper else TangledMapper()

    def build_node(self, blueprint, instance, arg_nodes=[]):
        if blueprint.is_value_node:
            return self.value_node_factory(blueprint, instance)
        elif blueprint.is_container_node:
            return self.container_node_factory(blueprint, instance, *arg_nodes)
        elif blueprint.is_method_call:
            return self.function_node_factory(blueprint, instance, instance, *arg_nodes)
        else:
            return self.function_node_factory(blueprint, instance, *arg_nodes)

    def build(self, original_instance, blueprint):
        to_build = deque([(original_instance, blueprint)])
        bricks = deque()
        while to_build:
            tangled_instance, blueprint = to_build.pop()
            if blueprint.node_for_other_class(tangled_instance):
                tangled_instance = self.mapper.get_mapped_object(tangled_instance,
                                                                 blueprint.owner_class)
            node = tangled_instance.nodes.get(blueprint.name, None)
            if node is None:
                bricks.append((tangled_instance, blueprint))
                if blueprint.input_count > 0:
                    for input_blueprint in blueprint.inputs():
                        to_build.append((tangled_instance, input_blueprint))
            else:
                bricks.append((tangled_instance, node))
        arg_stack = deque()
        last_node = None
        while bricks:
            tangled_instance, node_or_blueprint = bricks.pop()
            if isinstance(node_or_blueprint, NodeBlueprint):
                blueprint = node_or_blueprint
                func_args = deque()
                for i in range(blueprint.input_count):
                    func_args.appendleft(arg_stack.pop())
                last_node = self.build_node(blueprint, tangled_instance, func_args)
                tangled_instance.nodes[blueprint.name] = last_node
                arg_stack.append(last_node)
            else:
                last_node = node_or_blueprint
                arg_stack.append(last_node)
        return last_node

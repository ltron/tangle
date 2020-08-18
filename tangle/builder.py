""" Banan
"""
from collections import deque

from .nodes import FunctionNode, ValueNode
from .blueprints import NodeBlueprint, TangledSource, LinkBlueprint, MultiLinkBlueprint
from .mappers import TangledMapper

class BuildUnit(object):
    
    def __init__(self, instance, node_or_blueprint):
        self.instance = instance
        self.node_or_blueprint = node_or_blueprint


class TreeBuilder(object):

    def __init__(self,
                 function_node_factory=FunctionNode,
                 value_node_factory=ValueNode,
                 instance_mapper=None
                 ):
        self.function_node_factory = function_node_factory
        self.value_node_factory = value_node_factory
        self.mapper = instance_mapper if instance_mapper else TangledMapper()

    def build_node(self, blueprint, instance, arg_nodes = []):
        if blueprint.is_value_node:
            return self.value_node_factory(blueprint, instance)
        else:
            return self.function_node_factory(blueprint, instance, *arg_nodes)

    def build(self, original_instance, blueprint):
        """
        !!!!!!
        I think you can do this in one go by letting Nodes initialize without args
        so build node then append empty arg Node shells and so on

        """
        to_visit = deque([(original_instance, blueprint)])
        stack = []
        while to_visit:
            instance, blueprint = to_visit.pop()
            name = blueprint.name
            if isinstance(blueprint, TangledSource):

                node = instance.nodes.get(name, None)
                if node is None:
                    node = self.build_node(blueprint, instance)
                    instance.nodes[name] = node
                stack.append((None, node))
            elif isinstance(blueprint, LinkBlueprint):
                link = blueprint.method(instance)
                link_blueprint = link.get_blueprint(blueprint.blueprint_name)
                to_visit.append((link, link_blueprint))
            elif isinstance(blueprint, MultiLinkBlueprint):
                links = blueprint.method(instance)
                # Hur fan skall jag kunna fa till collection har?
                for link in links:
                    link_blueprint = link.get_blueprint(blueprint.blueprint_name)
                    to_visit.append((link, link_blueprint))
            elif isinstance(blueprint, NodeBlueprint):
                node = instance.nodes.get(name, None)
                if node is None:
                    stack.append((instance, blueprint))
                    for blueprint_arg in reversed(blueprint.blueprint_args):
                        to_visit.append((instance, blueprint_arg))
                else:
                    stack.append((None, node))
        args = []
        while stack:
            instance, blueprint = stack.pop()
            if instance:
                if blueprint.arg_count > 0:
                    _args = []
                    for _ in range(blueprint.arg_count):
                        _args.append(args.pop())
                    node = self.build_node(blueprint, instance, _args)
                else:
                    node = self.build_node(blueprint, instance, ())
                args.append(node)
            else:
                node = blueprint
                args.append(node)
        return node

    def new_build(self, original_instance, blueprint):
        """
        !!!!!!
        I think you can do this in one go by letting Nodes initialize without args
        so build node then append empty arg Node shells and so on

        """
        to_visit = deque([(original_instance, blueprint)])
        stack = []
        while to_visit:
            instance, blueprint = to_visit.pop()
            name = blueprint.name
            if isinstance(blueprint, TangledSource):
                node = instance.nodes.get(name, None)
                if node is None:
                    node = self.build_node(blueprint, instance)
                    instance.nodes[name] = node
                stack.append((None, node))
            elif isinstance(blueprint, LinkBlueprint):
                other_instance = blueprint.method(instance)
                if isinstance(other_instance, list):
                    for i in other_instance:
                        other_blueprint = i.get_blueprint(blueprint.blueprint_name)
                        to_visit.append((i, other_blueprint))
                else:
                    other_blueprint = other_instance.get_blueprint(blueprint.blueprint_name)
                    to_visit.append((i, other_blueprint))
            elif isinstance(blueprint, NodeBlueprint):
                node = instance.nodes.get(name, None)
                if node is None:
                    stack.append((instance, blueprint))
                    for blueprint_arg in reversed(blueprint.blueprint_args):
                        to_visit.append((instance, blueprint_arg))
                else:
                    stack.append((None, node))
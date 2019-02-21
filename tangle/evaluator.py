""" Module that implements an evaluator class. Used to traverse and
evaluate trees.
"""
import logging

from collections import deque

logger = logging.getLogger(__name__)


class Evaluator(object):

    def __init__(self):
        pass

    def evaluate(self, node):
        tree = deque([node])
        to_evaluate = deque()
        while tree:
            node = tree.pop()
            if node.is_value_node or not node.dirty:
                continue
            to_evaluate.append(node)
            for arg_node in node.arg_nodes:
                    tree.append(arg_node)
        while to_evaluate:
            node = to_evaluate.pop()
            node.calculate()

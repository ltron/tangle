import asyncio
import random

from tangle import Tangled, TreeBuilder, BasicEvaluator, tangled_function, tangled_map

Tangled.set_handlers(TreeBuilder(), BasicEvaluator())


@tangled_function
def fib(n):
    if n <= 1:
        return n
    a, b = 0, 1
    while i <= n:
        yield a
        a, b = b, a + b


class SubWork(Tangled):

    def __init__(self, n_work):
        self.n_work = n_work

    base_work = fib(self.n_work)

    derived_work = base_work - fib(self.n_work - 5)


class Work(Tangled):

    def __init__(self, name):
        self.name = name

    @tangled_link(SubWork)
    def sub_workers(self):
        return []

    work_from_children = tlist([sub_worker.derived_work for sub_worker in self.sub_workers])

    gathered_work = sum_of(work_from_children)


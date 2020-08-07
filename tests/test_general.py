import pytest
import logging

from tangle import Tangled, TreeBuilder, BasicEvaluator


def test_node():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    @Tangled.tangled_function
    def average(a, b):
        """ Decorator ensures that this function can be used in a Tangled graph
        """
        return (a + b) / 2

    class Foo(Tangled):
        source1 = TangledSource()
        source2 = TangledSource()

        foo_value = average(source1, source2)

        def __str__(self):
            return 'Foo<Instance>'

    class Bar(Tangled):

        def __init__(self, foo):
            super().__init__()
            self._foo = foo

        @Tangled.tangled_map(Foo)
        def my_foo(self):
            """ The decorator ensures that Bar can find Element objects in the Foo
            class
            """
            return self._foo

        # Define a source on Bar
        source1 = TangledSource()

        # Defines a bar Element that references Elements on Foo. This is how
        # nodes can be dependant on nodes in other objects
        bar_value = (source1 + my_foo.foo_value) / my_foo.source1

        def __str__(self):
            return 'Bar<Instance>'

    foo = Foo()
    bar = Bar(foo)

    foo.source1 = 5.0
    foo.source2 = 3.0

    bar.source1 = 6.0

    print(bar.bar_value)

def test_tmap():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    class Foo(Tangled):

        source1 = TangledSource()

        def __str__(self):
            return 'Foo<Instance>'
    
    foo1 = Foo()
    foo1.source1 = 2
    foo2 = Foo()
    foo2.source1 = 3

    class Bar(Tangled):

        def __init__(self, foos):
            super().__init__()
            self._foos = foos

        def foos(self):
            return self._foos

        bar_value = tmap(self.foos, 'source1')

    
    bar = Bar([foo1, foo2])

    print(bar.bar_value)
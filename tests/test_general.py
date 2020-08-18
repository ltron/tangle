import pytest
import logging

from tangle import Tangled, TreeBuilder, BasicEvaluator

def test_simple():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    class Foo(Tangled):

        source1 = TangledSource()
        source2 = TangledSource()

        foo_value = source1 + source2
    
    foo = Foo()

    foo.source1 = 1
    foo.source2 = 2
    value = foo.foo_value
    assert(value==3)

    foo.source1 = 3
    assert(foo.foo_value == 5)


def test_intraclass():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    @Tangled.tangled_function
    def average(a, b):
        """ Decorator ensures that this function can be used in a Tangled graph
        """
        return (a + b) / 2

    class Foo(Tangled):
        foo1 = TangledSource()
        foo2 = TangledSource()

        foo_value = average(foo1, foo2)

        def __str__(self):
            return 'Foo<Instance>'

    class Bar(Tangled):

        def __init__(self, foo):
            super().__init__()
            self._foo = foo

        @Tangled.link
        def my_foo(self):
            """ The decorator ensures that Bar can find Element objects in the Foo
            class
            """
            return self._foo

        # Define a source on Bar
        source1 = TangledSource()

        # Defines a bar Element that references Elements on Foo. This is how
        # nodes can be dependant on nodes in other objects
        bar_value = (source1 + my_foo.foo_value) / my_foo.foo1

        def __str__(self):
            return 'Bar<Instance>'

    foo = Foo()
    bar = Bar(foo)

    foo.foo1 = 5.0
    foo.foo2 = 3.0

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

        @Tangled.tangled_link
        def foos(self):
            return self._foos

        bar_value = tmap(foos, 'source1')

    
    bar = Bar([foo1, foo2])

    print(bar.bar_value)
import logging

from tangle import Tangled, TreeBuilder, BasicEvaluator, tangled_function, tangled_map


def test_node():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    @tangled_function
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

        @tangled_map(Foo)
        def my_foo(self):
            """ The decorator ensures that Bar can find Element objects in the Foo
            class
            """
            return self._foo

        # Define a source on Bar
        source1 = TangledSource()

        # Defines a bar Element that references Elements on Foo. This is how
        # nodes can be dependant on nodes in other objects
        bar_value = (source1 + Foo.foo_value) / Foo.source1

        def __str__(self):
            return 'Bar<Instance>'

    foo = Foo()
    bar = Bar(foo)

    foo.source1 = 5.0
    foo.source2 = 3.0

    bar.source1 = 6.0

    print(bar.bar_value)

from tangle import Tangled, TreeBuilder, BasicEvaluator, tangled_function, tangled_link


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

        @tangled_link(Foo)
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

    assert bar.bar_value == 2.0


def test_tlist():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    class Foo(Tangled):

        source1 = TangledSource()
        source2 = TangledSource()

        a_list = tlist([source1, source2])

    foo = Foo()

    foo.source1 = 5
    foo.source2 = 4

    assert sum(foo.a_list) == 9


def test_method_call():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    class Bar(Tangled):

        def method1(self):
            return 1

        def method2(self, var):
            return 2 * var

        source1 = TangledSource()

        calculation = self.method1() + self.method2(source1)

    bar = Bar()

    bar.source1 = 5

    assert bar.calculation == 11


def test_inheritance():

    Tangled.set_handlers(TreeBuilder(), BasicEvaluator())

    class Foo(Tangled):

        foo_test = TangledSource()

    class Bar(Foo):

        bar_test = TangledSource()

        result = bar_test + foo_test

    bar = Bar()
    bar.foo_test = 1.0
    bar.bar_test = 2.0

    print(isinstance(bar, Foo))
    assert bar.result == 3.0

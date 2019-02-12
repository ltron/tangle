from tangle import Tangled


def test_node():

    @Tangled.tangled_function
    async def do_stuff(a, b):
        """ Decorator ensures that this function can be used in a Tangled graph
        """
        return 10.0 * a / (4 * b)

    class Foo(Tangled):
        # Setup two sources
        source1 = TangledSource()
        source2 = TangledSource()

        #  Setup a function node with the sources as input
        foo_value = do_stuff(source1, source2)

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
        bar_value = (source1 - Foo.foo_value) / Foo.source1

    foo = Foo()
    bar = Bar(foo)

    foo.source1 = 1.0
    foo.source1 = 2.0

    bar.source1 = 0.5

    print(dir(bar))
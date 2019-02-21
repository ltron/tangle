
class TangledMapper(object):
    """ Class that implements relations between instances of one class to the other.
    """

    def __getitem__(self, item):
        raise NotImplementedError()

    def get_mapped_object(self, instance, other_class):
        try:
            return instance.tangled_maps[other_class](instance)
        except:
            my_class_name = instance.__class__.__name__
            other_class_name = other_class.__name__
            msg = f'No tangled map between {my_class_name} and {other_class_name}'
            raise MappingError(msg)

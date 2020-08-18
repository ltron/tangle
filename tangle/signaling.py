""" Funcationality that objects can inherit that allows them
to signal their dirtiness.
"""
from abc import ABCMeta

class Observer(object):

    def notify(self):
        raise NotImplementedError

class Dependable(object):

    def dependants(self):
        raise NotImplementedError

    def observers(self):
        raise NotImplementedError

    def notify_update(self):
        for dependable in self.dependants():
            dependable.set_dirty()
            dependable.notify_update()
        for observer in self.observers():
            observer.notify()
    
    def set_dirty(self):
        raise NotImplementedError

    def is_dirty(self):
        raise NotImplemented
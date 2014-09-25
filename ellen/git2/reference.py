# -*- coding: utf-8 -*-


class Reference(object):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)


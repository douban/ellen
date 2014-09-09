# -*- coding: utf-8 -*-

from pygit2 import init_repository as _init_repository


def init(path, bare=None):
    _init_repository(path, bare=bare)

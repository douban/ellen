# -*- coding: utf-8 -*-

from pygit2 import init_repository as _init_repository


def init_repository(path, work_path=None, bare=None):
    _init_repository(path, workdir_path=bare, bare=bare)

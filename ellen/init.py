#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import call2
from ellen.utils.process import GIT_EXECUTABLE


def init_repository(path, work_path=None, bare=None):
    if bare:
        return call2(GIT_EXECUTABLE, '--git-dir', path,
                     'init', '--bare')
    return call2(GIT_EXECUTABLE, '--git-dir', path,
                 '--work-tree', work_path, 'init')

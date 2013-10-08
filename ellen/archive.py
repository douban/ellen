#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils.process import call2
from utils.process import GIT_EXECUTABLE


def archive_repository(path, prefix, ref='master'):
    cmd = [GIT_EXECUTABLE, '--git-dir', path, 'archive']
    cmd.append('--prefix=%s/' % prefix)
    cmd.append(ref)
    return call2(cmd)

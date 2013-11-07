#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import call
from ellen.utils.process import call2
from ellen.utils.process import GIT_EXECUTABLE


def clone_repository(url, path, bare=None, checkout_branch=None, mirror=None,
                     env=None):
    cmd = [GIT_EXECUTABLE, 'clone']
    if checkout_branch:
        cmd.append('-b')
        cmd.append(checkout_branch)
    if bare:
        cmd.append('--bare')
    if mirror:
        cmd.append('--mirror')
    cmd.append(url)
    cmd.append(path)
    return call2(cmd, env=env)


def update_server_info(repository):
    return call(repository, 'update-server-info')

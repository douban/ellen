#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shlex
import logging
import subprocess
import collections

GIT_EXECUTABLE = 'git'
GIT_DIR_DEFAULT = '.git'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _shlex_split(cmd):
    if isinstance(cmd, unicode):
        return [c.decode("utf-8") for c in shlex.split(cmd.encode("utf-8"))]
    elif isinstance(cmd, str):
        return shlex.split(cmd.encode("utf-8"))
    elif not isinstance(cmd, list):
        return list(cmd)
    return cmd


def _call(cmd, env=None):
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=env)
    except (OSError, TypeError) as err:
        logger.error("Error occurrred when calling %s" % " ".join(cmd))
        raise err
    out, err = process.communicate()
    out = str(out)
    err = str(err)

    result = {}

    result['returncode'] = process.returncode
    result['stdout'] = out
    result['stderr'] = err
    result['fullcmd'] = " ".join(cmd)
    return result


# TODO: remove repository.
def call(repository, cmd, env=None):
    cmd = _shlex_split(cmd)
    git_dir = repository.path.rstrip('/')
    work_dir = '/'.join(git_dir.split('/')[:-1])
    add2cmd = ['--git-dir', git_dir]
    if not repository.is_bare:
        add2cmd += ['--work-tree', work_dir]
    return _call([GIT_EXECUTABLE] + add2cmd + cmd, env=env)


# TODO: use call instead
def call2(*args, **kwargs):
    """System calls with string or list args"""
    env = kwargs.pop('env', {})
    assert not kwargs, "call kwargs not understood in %s" % kwargs
    fullcmd = []
    if len(args) == 1:
        cmd = args[0]
    else:
        cmd = args
    cmd = _shlex_split(cmd)
    # flatten
    fullcmd = []
    for el in cmd:
        if isinstance(el, basestring):
            fullcmd.append(el)
        elif isinstance(el, collections.Iterable):
            fullcmd.extend(el)
        else:
            fullcmd.append(str(el))
    assert len(fullcmd) >= 1, "Need to pass at least a command"
    return _call(fullcmd, env=env)

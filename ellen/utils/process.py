#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shlex
import logging
import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: remove this?
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


# TODO: add tests or doctests
class Process(object):
    def __init__(self, cmds=None):
        self.cmds = cmds or []

    def __getattr__(self, name):
        name = name.replace('_', '-')  # e.g. format_patch -> format-patch
        return self.bake(name)

    def __call__(self, *a, **kw):
        proc = self.bake()
        env = kw.pop('env', {})
        proc._parse_args(*a, **kw)
        return proc.call(env=env)

    def _parse_args(self, *a, **kw):
        cmds = []
        for p in a:
            if not isinstance(p, (str, unicode)):
                raise KeyError
            cmds.append(p)

        for k, v in kw.iteritems():
            if len(k) == 1:
                k = '-' + k
            else:
                k = '--' + k
            if '_' in k:  # e.g. --no_ff -> --no-ff
                k = k.replace('_', '-')
            if not v:  # v in (None, '', False)
                continue
            elif isinstance(v, bool):  # v is True
                cmds.append(k)
            # FIXME: command line args may be unicode string
            elif isinstance(v, (str, unicode)):
                cmds.append(k)
                cmds.append(v)
            else:
                raise KeyError
        self.cmds += cmds

    def bake(self, *a, **kw):
        cmds = list(self.cmds)
        proc = Process(cmds)
        proc._parse_args(*a, **kw)
        return proc

    def call(self, cmdstr='', env=None):
        extra_cmds = _shlex_split(cmdstr)
        return _call(self.cmds + extra_cmds, env=env)


process = Process()
git = process.bake('git')


def git_with_path(git_dir=None, work_tree=None):
    baked = git.bake()
    if git_dir:
        baked = baked.bake('--git-dir', git_dir)
    if work_tree:
        baked = baked.bake('--work-tree', work_tree)
    return baked


def git_with_repo(repository):
    git_dir = repository.path
    work_tree = repository.workdir
    return git_with_path(git_dir, work_tree)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import subprocess
from ..process import git

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

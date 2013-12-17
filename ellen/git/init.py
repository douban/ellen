#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_path


# FIXME: 比较 `git init` 跟 `pygit2.init_repository`
def init_repository(path, work_path=None, bare=None):
    """git init command"""
    git = git_with_path(git_dir=path, work_tree=work_path)
    git.init(bare=bare)

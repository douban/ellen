# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_path


def init_repository(path, work_path=None, bare=None):
    """git init command"""
    git = git_with_path(git_dir=path, work_tree=work_path)
    git.init(bare=bare)

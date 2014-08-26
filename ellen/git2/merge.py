# -*- coding: utf-8 -*-

from ellen.process import git_with_repo


def merge(repository, *k, **kw):
    git = git_with_repo(repository)
    return git.merge(*k, **kw)

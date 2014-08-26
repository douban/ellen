# -*- coding: utf-8 -*-

from ellen.process import git_with_repo


def fetch(repository, *w, **kw):
    git = git_with_repo(repository)
    return git.fetch(*w, **kw)

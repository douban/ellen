# -*- coding: utf-8 -*-

from ellen.process import git_with_repo


def fetch2(repository, *w, **kw):
    git = git_with_repo(repository)
    return git.fetch(*w, **kw)


def fetch(repository, name):
    remotes = {remote.name: remote
               for remote in repository.remotes}
    if name:
        remotes[name].fetch()
        return None
    for key in remotes:
        remotes[key].fetch()

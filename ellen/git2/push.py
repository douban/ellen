# -*- coding: utf-8 -*-

from ellen.process import git_with_repo


def push(repository, remote, ref, _env=None):
    git = git_with_repo(repository)
    return git.push(remote, ref, env=_env)

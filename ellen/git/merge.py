#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo


# FIXME: param _raise ??
def merge(repository, ref, msg='automerge', commit_msg='',
          no_ff=False, _raise=True, _env=None):
    # msg, commit_msg makes multiline commit message
    git = git_with_repo(repository)
    git_merge = git.bake('merge', ref, no_ff=no_ff)
    if msg:
        git_merge = git_merge.bake(m=msg)
    if commit_msg:
        git_merge = git_merge.bake(m=commit_msg)
    return git_merge(env=_env)

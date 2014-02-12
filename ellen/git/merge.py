#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo
from ellen.utils.format import format_merge_result, format_index


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

def merge_tree(repository, ours, theirs):
    theirs = repository.revparse_single(theirs)
    theirs_tree = theirs.tree
    ours = repository.revparse_single(ours)
    ours_tree = ours.tree
    merge_base = repository.merge_base(theirs.hex,
                                       ours.hex)
    merge_base_tree = repository.get(merge_base.hex).tree
    index = ours_tree.merge(theirs_tree, merge_base_tree)
    return format_index(index)

def merge_head(repository, ref):
    target = repository.revparse_single(ref)
    oid = target.id
    merge_result = repository.merge(oid)
    return format_merge_result(merge_result)

def merge_commits(repository, ours, theirs):
    theirs = repository.revparse_single(theirs)
    ours = repository.revparse_single(ours)
    merge_index = repository.merge_commits(ours, theirs)
    return format_index(merge_index)

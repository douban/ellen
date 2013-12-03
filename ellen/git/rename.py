#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_DIFF_REVERSE


# TODO: move to diff or util
def detect_renamed(repository, ref, path=None):
    """Find renamed files in the commit diff."""
    commit = repository.revparse_single(ref)
    parents = commit.parents
    if len(parents) == 0:
        opt = GIT_DIFF_REVERSE
        diff = commit.tree.diff(flags=opt, empty_tree=True)
    else:
        parent = parents[0]
        diff = parent.tree.diff(commit.tree)
    diff.find_similar()
    result = dict((d.new_file_path, d.old_file_path)
                  for d in diff if d.status == "R")
    return result

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_SORT_TIME
from pygit2 import GIT_SORT_TOPOLOGICAL

from ellen.utils.format import format_commit


def rev_list(repository, to_ref, from_ref=None, path=None, skip=0,
             max_count=0, author=None, query=None, first_parent=None,
             since=0, no_merges=None):
    """git rev-list command, pygit2 wrapper.
    But this returns a commit list"""

    if repository.is_empty:
        return []

    commits_index_list = []
    commits_dict = {}
    # TODO: use resolve_version
    to_commit = repository.revparse_single(to_ref)

    walk_order = GIT_SORT_TOPOLOGICAL if first_parent else GIT_SORT_TIME
    if to_commit.type == GIT_OBJ_TAG:
        to_commit = repository[to_commit.target]
    next_commit = None
    walker = repository.walk(to_commit.id, walk_order)
    if from_ref:
        try:
            from_commit = repository.revparse_single(from_ref)
            if from_commit.type == GIT_OBJ_TAG:
                from_commit = repository[from_commit.target]
            walker.hide(from_commit.id)
        except (KeyError, ValueError):
            from_commit = None

    if max_count:
        length = max_count + skip if skip else max_count
    else:
        length = 0
    for c in walker:
        if all([_check_author(c, author),
                _check_file_change(c, path),
                _check_message(c, query),
                _check_date(c, since),
                _check_no_merges(c, no_merges)]):
            index = c.hex
            if first_parent:
                if next_commit and next_commit.hex != c.hex:
                    continue
                if len(c.parents) == 0:
                    next_commit = None
                elif len(c.parents) >= 1:
                    next_commit = c.parents[0]
                else:
                    continue
            if index not in commits_index_list:
                commits_index_list.append(index)
            commits_dict[index] = c
        if length and len(commits_index_list) >= length:
            break
    if skip:
        commits_index_list = commits_index_list[skip:]
    return [format_commit(commits_dict[i], repository)
            for i in commits_index_list]


def _check_author(commit, author):
    """check author or email"""
    if author and commit.author.name == author:
        return True
    elif author and commit.author.email == author:
        return True
    elif not author:
        return True
    return False


# FIXME: time & offset ?
def _check_date(commit, since):
    if since and commit.committer.time > since:
        return True
    elif not since:
        return True
    return False


def _check_no_merges(commit, no_merges):
    if no_merges and len(commit.parents) <= 1:
        return True
    elif not no_merges:
        return True
    return False


# no use yet
def _check_path(tree, path):
    try:
        entry = tree[path]
    except KeyError:
        return None
    return entry


def _check_message(commit, query):
    if query and query in commit.message:
        return True
    elif not query:
        return True


# FIXME: add quick diff
def _check_file_change(commit, path):
    if path and commit.is_changed([path], no_diff=True)[0]:
        return True
    #commit_tree = commit.tree
    #parents = commit.parents
    #if path and _check_path(commit_tree, path):
    #    count = 0
    #    c_entry = commit_tree[path]
    #    for p in parents:
    #        parent_tree = p.tree
    #        if commit_tree.id == parent_tree.id:
    #            return False
    #        p_entry = _check_path(parent_tree, path)
    #        if not p_entry:
    #            count += 1
    #            continue
    #        if p_entry.id != c_entry.id:
    #            count += 1
    #    if count == len(parents):
    #        return True
    elif not path:
        return True

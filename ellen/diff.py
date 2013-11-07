#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_OBJ_COMMIT

from ellen.utils import JagareError
from ellen.utils.git import _resolve_version


def diff(repository, ref, from_ref=None, **kwargs):
    # TODO: add merge_base support
    _diff = {}
    ref = ref.strip()
    sha = _resolve_version(repository, ref)
    if not sha:
        raise JagareError("%s...%s" % (from_ref, ref))
    commit = get_commit_by_sha(repository, sha)
    from_commit = None
    if from_ref:
        from_ref = from_ref.strip()
        from_sha = _resolve_version(repository, from_ref)
        if not from_sha:
            raise JagareError("%s...%s" % (from_ref, ref))
        from_commit = get_commit_by_sha(repository, from_sha)
    # get pygit2 diff
    if from_commit:
        diff, _diff['old_sha'] = diff_commits(repository, commit, from_commit,
                                              **kwargs)
    else:
        diff, _diff['old_sha'] = diff_commit(repository, commit, **kwargs)
    _diff['new_sha'] = commit.hex
    _diff['diff'] = diff
    return _diff


def diff_commits(repository, commit, from_commit=None, **kwargs):
    tree = commit.tree
    from_tree = from_commit.tree if from_commit else None
    # call pygit2 diff
    if from_tree:
        diff = repository.diff(from_tree, tree, **kwargs)
        old_sha = from_commit.hex
    else:
        diff = tree.diff_to_tree(swap=True, **kwargs)
        old_sha = None
    return diff, old_sha


def diff_commit(repository, commit, **kwargs):
    ''' one commit, default diff with parent '''
    parents = commit.parents
    if len(parents) >= 1:
        diff = diff_commits(repository, commit, parents[0], **kwargs)
    else:
        diff = diff_commits(repository, commit, **kwargs)
    return diff


def get_commit_by_sha(repository, sha):
    try:
        commit = repository[sha]
    except (ValueError, KeyError, TypeError):
        raise JagareError("Commit '%s' is invalid." % sha)

    if commit and commit.type == GIT_OBJ_COMMIT:
        return commit

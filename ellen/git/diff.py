#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_OBJ_COMMIT
from pygit2 import GIT_DIFF_IGNORE_WHITESPACE

from ellen.utils import JagareError
from ellen.utils.git import resolve_version
from ellen.utils.format import format_diff


# TODO: remove path, use paths instead
# FIXME: make args explicit
def diff_wrapper(repository, *w, **kw):
    """Jagare's diff wrapper,
    :param ref:
    :param from_ref:
    :param ignore_space:
    :param flags:
    :param context_lines:
    :param path:
    :param paths:
    :param rename_detection:
    """
    try:
        kws = {}
        ignore_space = kw.get('ignore_space', None)
        if ignore_space:
            flags = kw.get('flags', 0)
            flags |= GIT_DIFF_IGNORE_WHITESPACE
            kws.update({'flags': flags})
        from_ref = kw.get('from_ref', None)
        if from_ref:
            kws.update({'from_ref': from_ref})
        context_lines = kw.get('context_lines', None)
        if context_lines:
            kws.update({'context_lines': context_lines})
        path = kw.get('path', None)
        paths = kw.get('paths', None)
        if path:
            kws.update({'paths': [path]})
        if paths:
            kws.update({'paths': paths})

        d = diff(repository, *w, **kws)
        rename_detection = kw.get('rename_detection', None)
        if rename_detection:
            d['diff'].find_similar()

        return format_diff(d)

    except JagareError:
        return {}


def diff(repository, ref, from_ref=None, **kwargs):
    """git diff command, pygit2 wrapper
    :param ref:
    :param from_ref:
    :param flags:
    :param context_lines:
    :param paths:
    """

    _diff = {}
    ref = ref.strip()
    sha = resolve_version(repository, ref)
    if not sha:
        raise JagareError("%s...%s" % (from_ref, ref))
    commit = get_commit_by_sha(repository, sha)
    from_commit = None
    if from_ref:
        from_ref = from_ref.strip()
        from_sha = resolve_version(repository, from_ref)
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
    """ one commit, default diff with parent """
    parents = commit.parents
    if len(parents) == 1:
        diff = diff_commits(repository, commit, parents[0], **kwargs)
    elif len(parents) == 2:
        merge_base_hex = repository.merge_base(parents[0].hex, parents[-1].hex)
        merge_base = repository[merge_base_hex] if merge_base_hex else commit
        diff = diff_commits(repository, parents[-1], merge_base, **kwargs)
    elif len(parents) > 2:
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

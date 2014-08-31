# -*- coding: utf-8 -*-

from pygit2 import GIT_DIFF_IGNORE_WHITESPACE
from ellen.git2.commit import resolve_commit


def diff(repository, reference, from_reference=None,
         paths=None,
         ignore_space=None,
         context_lines=3,
         rename_detection=None):
    flags = 0
    if ignore_space:
        flags |= GIT_DIFF_IGNORE_WHITESPACE

    if not from_reference:
        commit = resolve_commit(reference)
        from_reference, reference = diff_commit(commit)

    if not from_reference:
        d = commit.tree.diff_to_tree(swap=True, flags=flags,
                                     context_lines=context_lines)
    else:
        d = repository.diff(a=from_reference, b=reference,
                            flags=flags,
                            context_lines=context_lines)

    if rename_detection:
        d.find_similar()

    return d


def diff_commit(repository, commit):
    parents = commit.parents
    if len(parents) == 1:
        return parents[0], commit
    elif len(parents) == 2:
        merge_base_hex = repository.merge_base(parents[0].hex, parents[-1].hex)
        merge_base = repository[merge_base_hex] if merge_base_hex else commit
        return merge_base, parents[-1]
    elif len(parents) > 2:
        return parents[0], commit
    else:
        return None, commit


def diff_tree():
    pass


def diff_blob():
    pass

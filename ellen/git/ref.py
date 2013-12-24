#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_REF_OID
from pygit2 import GIT_REF_SYMBOLIC
from pygit2 import Signature

from ellen.utils import JagareError


def update_ref(repository, ref, newvalue):
    """git update-ref/symbolic-ref command, pygit2 wrapper.

    :param ref: the full name of the reference/symbolic ref.
    :param newvalue: the sha-1 value of the commit
                      or the full name of the target reference."""
    # TODO: support for no-deref option
    # git update-ref
    if repository.is_empty:
        raise JagareError("repository is empty")

    try:
        commit = repository.revparse_single(newvalue)
    except KeyError:
        raise JagareError("newvalue is invalid.")
    except Exception:
        raise JagareError("refs not found.")

    try:
        repo_ref = repository.lookup_reference(ref)
    except KeyError:
        repository.create_reference(ref, commit.hex)
        return

    if repo_ref.type == GIT_REF_OID:
        try:
            repo_ref.target = commit.hex
        except OSError:
            raise JagareError("OSError occurred because of concurrency,"
                              " try again later")

    # TODO: change acting when the reference is symbolic
    elif repo_ref.type == GIT_REF_SYMBOLIC:
        # WARNING: this else is acting like `git symbolic-ref`
        try:
            repo_new = repository.lookup_reference(newvalue)
        except Exception:
            raise JagareError("refs not found.", 400)
        repo_ref.target = repo_new.name


def delete_ref():
    pass


def append_reflog(repository, reference, name, email, message):
    try:
        ref = repository.lookup_reference(reference)
    except KeyError:
        return True
    committer = Signature(name, email)
    ref.append_log(committer, message)

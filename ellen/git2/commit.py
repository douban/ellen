# -*- coding: utf-8 -*-

from pygit2 import (GIT_OBJ_TAG,
                    GIT_OBJ_BLOB,
                    GIT_OBJ_TREE,
                    GIT_OBJ_COMMIT)
from ellen.git2.rev_list import rev_list


def resolve_commit(repository, reference):
    try:
        obj = repository.revparse_single(reference)
        if obj.type == GIT_OBJ_TAG:
            commit = repository[obj.target]
        elif obj.type == GIT_OBJ_COMMIT:
            commit = obj
        elif obj.type == GIT_OBJ_BLOB:
            return None
        elif obj.type == GIT_OBJ_TREE:
            return None
    except KeyError:
        return None
    except ValueError:
        return None
    return commit


def list_commits(repository, *k, **kw):
    return rev_list(repository, *k, **kw)

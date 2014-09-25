# -*- coding: utf-8 -*-

from pygit2 import (GIT_OBJ_TAG,
                    GIT_OBJ_BLOB,
                    GIT_OBJ_TREE,
                    GIT_OBJ_COMMIT)

PYGIT2_OBJ_TYPE = {
    GIT_OBJ_TAG: 'tag',
    GIT_OBJ_BLOB: 'blob',
    GIT_OBJ_TREE: 'tree',
    GIT_OBJ_COMMIT: 'commit',
}


def resolve_type(repository, version):
    try:
        obj = repository.revparse_single(version)
        type = PYGIT2_OBJ_TYPE[obj.type]
    except KeyError:
        type = None
    except ValueError:
        type = None
    return type

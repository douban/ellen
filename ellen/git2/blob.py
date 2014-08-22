# -*- coding: utf-8 -*-

from pygit2 import (GIT_OBJ_TAG,
                    GIT_OBJ_BLOB,
                    GIT_OBJ_TREE,
                    GIT_OBJ_COMMIT)


def resolve_blob(repository, reference):
    try:
        obj = repository.revparse_single(reference)
        if obj.type == GIT_OBJ_TAG:
            return None
        elif obj.type == GIT_OBJ_COMMIT:
            return None
        elif obj.type == GIT_OBJ_BLOB:
            return obj
        elif obj.type == GIT_OBJ_TREE:
            return None
    except KeyError:
        return None
    except ValueError:
        return None

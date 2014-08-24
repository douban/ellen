# -*- coding: utf-8 -*-

from pygit2 import (GIT_OBJ_TAG,
                    GIT_OBJ_BLOB,
                    GIT_OBJ_TREE,
                    GIT_OBJ_COMMIT)


def list_entries(repository, reference, path=None, recursive=None):
    rs = {}
    tree = get_tree(repository, reference, path)
    walker = _walk_tree(tree, path)
    for index, (entry, path) in enumerate(walker):
        path = "%s/%s" % (path, entry.name) if path else entry.name
        if recursive and entry.type == GIT_OBJ_TREE:
            _tree = repository[entry.id]
            _tree_list = _walk_tree(_tree, path)
            for _index, _entry in enumerate(_tree_list):
                walker.insert(index + _index + 1, _entry)
        rs[path] = Entry(entry)
    return rs


def get_tree(repository, reference, path):

    try:
        obj = repository.revparse_single(reference)
    except (ValueError, KeyError):
        # TODO add ellen error
        raise ValueError("Reference not found.")

    commit_obj = None

    if obj.type == GIT_OBJ_TREE:
        tree_obj = obj
    elif obj.type == GIT_OBJ_TAG:
        commit_obj = repository.revparse_single(obj.target.hex)
        tree_obj = commit_obj.tree
    elif obj.type == GIT_OBJ_BLOB:
        # TODO add ellen error
        raise ValueError("Object is blob, doesn't contain any tree")
    elif obj.type == GIT_OBJ_COMMIT:
        commit_obj = obj
        tree_obj = obj.tree

    if path:
        return tree_obj[path]

    return tree_obj


def _walk_tree(tree, path=None):
    entry_list = []
    for entry in tree:
        entry_list.append((entry, path))
    return entry_list


class Entry(object):

    def __init__(self, entry):
        self.id = entry.id
        self.hex = entry.hex
        self.type = entry.type
        self.name = entry.name
        self.filemode = entry.filemode

    @property
    def is_commit(self):
        return self.type == GIT_OBJ_COMMIT
        pass

    @property
    def is_blob(self):
        return self.type == GIT_OBJ_BLOB

    @property
    def is_tree(self):
        return self.type == GIT_OBJ_TREE

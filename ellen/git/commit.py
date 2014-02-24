#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_FILEMODE_BLOB_EXECUTABLE
from pygit2 import GIT_FILEMODE_BLOB
from pygit2 import Signature

from ellen.utils import JagareError
from ellen.utils.tree_node import init_root


# FIXME: always return empty list
def create_commit(repository, branch, parent,
                  author_name, author_email,
                  message, reflog, data):
    """git commit command, pygit2 wrapper.
    :param parent: parent ref
    :param data: list of tuple(filepath, content, action),
        action is insert/remove"""
    if repository.is_empty:
        if branch != "master" or parent != "master":
            raise JagareError("only commit to master when repo is empty")

    parents_sha = []
    parent_commit = None
    if not repository.is_empty:
        parent_commit = repository.revparse_single(parent)
        parents_sha.append(str(parent_commit.id))

    ret = []
    flag = False
    root = init_root()
    for filepath, content, action in data:
        content = unicode_to_utf8(content)
        content = content.replace("\r\n", "\n")
        if action == "insert":
            root.add_file(filepath, content)
        elif action == "remove":
            root.del_file(filepath)
        else:
            root.add_file(filepath, content)
        #filepath = unicode_to_utf8(filepath)
        #mode = _get_pygit2_mode(mode)
        flag = True

    # FIXME: remove this after refactor gist
    #if not flag:
    #    root.add_file('empty', '')
    #    flag = True

    if flag:
        for entry in root.walk():
            entry.write(repository, parent_commit if parent_commit else None)
        tree_oid = root.id
        signature = Signature(author_name, author_email)
        commit_oid = repository.create_commit("refs/heads/%s" % branch,
                                          signature, signature, message,
                                          tree_oid, parents_sha)
        master = repository.lookup_reference("refs/heads/%s" % branch)
        master.target = str(commit_oid)
        master.log_append(str(commit_oid), signature, reflog)
        return ret
    return []


def _get_pygit2_mode(mode):
    if mode == "100755":
        return GIT_FILEMODE_BLOB_EXECUTABLE
    return GIT_FILEMODE_BLOB


def unicode_to_utf8(c):
    if isinstance(c, unicode):
        c = c.encode('utf8')
    return c

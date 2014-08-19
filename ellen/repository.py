# -*- coding: utf-8 -*-

import os
from pygit2 import Repository as _Repository
from ellen.git2.init import init_repository
from ellen.git2.entry import list_entries


class Repository(object):

    def __init__(self, path):
        self._pygit2_repository = _Repository(path)
        self._git = None

    # Repository
    @classmethod
    def init_repository(cls, path, work_path=None, bare=None):
        # if parent dir not exist, create it.
        if not os.path.exists(path):
            os.makedirs(path)
        init_repository(path, work_path=work_path, bare=bare)
        return cls(path)

    @classmethod
    def clone_repository(cls):
        return

    @classmethod
    def import_repository(cls):
        return

    @classmethod
    def mirror_repository(cls):
        return

    # Remote
    def list_remotes(self):
        return

    def create_remote(self):
        return

    # Reference
    def list_references(self):
        return

    def lookup_reference(self):
        return

    def update_reference(self):
        return

    # Tag
    def list_tags(self):
        return

    def create_tag(self):
        return

    # Branch
    def list_branches(self):
        return self._pygit2_repository.listall_branches()

    def create_branch(self):
        return

    def delete_branch(self):
        return

    # Tree
    def list_trees(self):
        return

    def list_entries(self, *k, **kw):
        return list_entries(self._pygit2_repository, *k, **kw)

    # Hook
    def patch_hook(self, path):
        pass

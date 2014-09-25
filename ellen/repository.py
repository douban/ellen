# -*- coding: utf-8 -*-

import os
from pygit2 import Repository as _Repository
from ellen.git.ref import update_ref
from ellen.git2.entry import list_entries
from ellen.git2.commit import resolve_commit, list_commits
from ellen.git2.object import resolve_type
from ellen.git2.blob import resolve_blob
from ellen.git2.tag import list_tags
from ellen.git2.branch import list_branches
# porcelain
from ellen.git2.fetch import fetch
from ellen.git2.init import init
from ellen.git2.push import push
from ellen.git2.merge import merge
from ellen.git2.diff import diff
from ellen.git.blame import blame
from ellen.git2.clone import clone, clone_to


class Repository(object):

    def __init__(self, path):
        self._pygit2_repository = _Repository(path)
        self._git = None

    @property
    def is_empty(self):
        return self._pygit2_repository.is_empty

    @property
    def is_bare(self):
        return self._pygit2_repository.is_bare

    # Repository
    @classmethod
    def init(cls, path, bare=None):
        # if parent dir not exist, create it.
        if not os.path.exists(path):
            os.makedirs(path)
        init(path, bare=bare)
        return cls(path)

    @classmethod
    def clone(cls, *k, **kw):
        return clone(*k, **kw)

    def clone_to(self, *k, **kw):
        return clone_to(self._pygit2_repository, *k, **kw)

    @classmethod
    def import_repository(cls):
        return

    @classmethod
    def mirror_repository(cls):
        return

    # Remote
    def list_remotes(self):
        return self.repository.remotes

    def create_remote(self, name, url):
        return self.repository.create_remote(name, url)

    # Reference
    def list_references(self):
        return

    def lookup_reference(self):
        return

    def update_reference(self, reference, newvalue):
        return update_ref(self._pygit2_repository, reference, newvalue)

    # Tag
    def list_tags(self):
        return list_tags(self._pygit2_repository)

    def create_tag(self):
        return

    # Branch
    def list_branches(self):
        return list_branches(self._pygit2_repository)

    def create_branch(self):
        return

    def delete_branch(self):
        return

    # Tree
    def list_trees(self):
        return

    def list_entries(self, *k, **kw):
        return list_entries(self._pygit2_repository, *k, **kw)

    def resolve_entry(self, reference):
        return self._pygit2_repository.revparse_single(reference)

    # Commit
    def list_commits(self, *k, **kw):
        return list_commits(self._pygit2_repository, *k, **kw)

    def resolve_commit(self, reference):
        return resolve_commit(self._pygit2_repository, reference)

    def resolve_blob(self, reference):
        return resolve_blob(self._pygit2_repository, reference)

    def resolve_type(self, reference):
        return resolve_type(self._pygit2_repository, reference)

    # Hook
    def patch_hook(self, path):
        pass

    # Porcelain
    def push(self, *k, **kw):
        return push(self._pygit2_repository, *k, **kw)

    def merge(self, *k, **kw):
        return merge(self._pygit2_repository, *k, **kw)

    def fetch(self, *k, **kw):
        return fetch(self._pygit2_repository, *k, **kw)

    def diff(self, *k, **kw):
        return diff(self._pygit2_repository, *k, **kw)

    def blame(self, *k, **kw):
        return blame(self._pygit2_repository, *k, **kw)

    def merge_base(self, reference, from_reference):
        return self._pygit2_repository.merge_base(reference, from_reference)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from pygit2 import Repository
from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_BLOB
from pygit2 import GIT_OBJ_TREE
from pygit2 import GIT_OBJ_COMMIT

from ellen.utils import JagareError
from ellen.utils.git import format_blob
from ellen.utils.git import format_tree
from ellen.utils.git import format_commit
from ellen.utils.git import format_tag
from ellen.utils.git import _resolve_version
from ellen.utils.git import _resolve_type
from ellen.git.tree import ls_tree
from ellen.git.rev_list import rev_list
from ellen.git.rename import detect_renamed
from ellen.git.tag import list_tags
from ellen.git.commit import create_commit
from ellen.git.diff import diff_wrapper as diff
from ellen.git.ref import update_ref
from ellen.git.clone import clone_repository, update_server_info
from ellen.git.init import init_repository
from ellen.git.archive import archive_repository
from ellen.git.blame import blame
from ellen.git.format_patch import format_patch
from ellen.git.merge import merge
from ellen.git.push import push


class Jagare(object):
    ''' pygit2 and git commands wrapper '''

    def __init__(self, path):
        self.repository = repository(path)
        self.repository_name = None

    def __eq__(self, other):
        if isinstance(other, Jagare):
            return self.path == other.path
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.path)

    @property
    def path(self):
        return self.repository.path

    @property
    def empty(self):
        return self.repository.is_empty

    @property
    def bare(self):
        return self.repository.is_bare

    @property
    def head(self):
        if self.repository.is_empty:
            return None
        return self.repository.head

    @property
    def branches(self):
        """return a list of branch names"""
        return self.list_branches()

    @property
    def tags(self):
        return self.list_tags(name_only=True)

    # TODO: change to property
    def remotes(self):
        return self.repository.remotes

    def list_tags(self, *w, **kw):
        return list_tags(self.repository, *w, **kw)

    def list_branches(self):
        branches = self.repository.listall_branches()
        return branches

    def show(self, ref):
        try:
            obj = self.repository.revparse_single(ref)
        except KeyError:
            return {}
        obj_type = obj.type

        # TODO: formatter
        if obj_type == GIT_OBJ_COMMIT:
            return format_commit(ref, obj, self.repository)
        elif obj_type == GIT_OBJ_TAG:
            return format_tag(ref, obj, self.repository)
        elif obj_type == GIT_OBJ_TREE:
            return format_tree(ref, obj, self.repository)
        elif obj_type == GIT_OBJ_BLOB:
            return format_blob(ref, obj, self.repository)

    def ls_tree(self, ref, path=None, recursive=False, size=None,
                with_commit=False):
        return ls_tree(self.repository, ref, req_path=path,
                       recursive=recursive, size=size, with_commit=with_commit)

    def rev_list(self, *w, **kw):
        commits = []
        try:
            commits = rev_list(self.repository, *w, **kw)
        except KeyError:
            # FIXME: use JagareError
            pass
        return commits

    def blame(self, ref, path, lineno=None):
        result = blame(self.repository, ref, path, lineno)
        return self.show(ref), result

    def format_patch(self, ref, from_ref=None):
        return format_patch(self.repository, ref, from_ref)

    def detect_renamed(self, ref, path=None):
        return detect_renamed(self.repository, ref)

    def commit_file(self, *w, **kw):
        return create_commit(self.repository, *w, **kw)

    def diff(self, *w, **kw):
        return diff(self.repository, *w, **kw)

    def resolve_commit(self, version):
        version = version.strip()
        return _resolve_version(self.repository, version)

    def resolve_type(self, version):
        version = version.strip()
        return _resolve_type(self.repository, version)

    # TODO: cls.clone_from

    @classmethod
    def _clone(cls, url, path, bare=None, branch=None, mirror=None,
               env=None):
        # TODO: check clone result
        clone_repository(url, path,
                         bare=bare, checkout_branch=branch,
                         mirror=mirror, env=env)
        jagare = Jagare(path)
        if bare:
            update_server_info(jagare.repository)
        return jagare

    def clone(self, path, bare=None, branch=None, mirror=None, env=None):
        return self._clone(self.repository.path, path,
                           bare=bare, branch=branch,
                           mirror=mirror, env=env)

    @classmethod
    def mirror(cls, url, path, bare=None, branch=None, env=None):
        return cls._clone(url, path,
                          bare=bare, branch=branch,
                          mirror=True, env=env)

    @classmethod
    def init(cls, path, work_path=None, bare=None):
        # TODO: move to libs
        # if parent dir not exist, create it.
        if not os.path.exists(path):
            os.makedirs(path)
        init_repository(path, work_path=work_path, bare=bare)
        return cls(path)

    def listall_references(self):
        return self.repository.listall_references()

    def lookup_reference(self, *w, **kw):
        return self.repository.lookup_reference(*w, **kw)

    def add_remote(self, name, url):
        self.repository.create_remote(name, url)

    def update_ref(self, ref, newvalue):
        return update_ref(self.repository, ref, newvalue)

    def update_head(self, branch_name):
        branch = self.repository.lookup_branch(branch_name)
        if not branch:
            return None
        self.update_ref('HEAD', branch.name)

    def sha(self, rev='HEAD'):
        return _resolve_version(self.repository, rev)

    def merge_base(self, to_sha, from_sha):
        return self.repository.merge_base(to_sha, from_sha)

    def fetch_all(self):
        for remote in self.remotes():
            remote.fetch()

    def fetch(self, name):
        target = {remote.name: remote for remote in self.remotes()}.get(name)
        if target:
            target.fetch()

    def merge(self, ref, msg='automerge', commit_msg='',
              no_ff=False, _raise=True, _env=None):
        return merge(self.repository, ref, msg, commit_msg,
                     no_ff, _raise, _env)

    def push(self, remote, ref, _env=None):
        return push(self.repository, remote, ref, _env=_env)

    def archive(self, prefix):
        result = archive_repository(self.repository.path, prefix)
        return result['stdout']

    def delete_branch(self, name):
        branch = self.repository.lookup_branch(name)
        if branch:
            branch.delete()


def repository(path):
    try:
        repo = Repository(path)
    except KeyError:
        raise JagareError('repo %s not exists' % path)
    return repo

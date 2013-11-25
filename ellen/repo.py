#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from pygit2 import Repository
from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_BLOB
from pygit2 import GIT_OBJ_TREE
from pygit2 import GIT_OBJ_COMMIT
from pygit2 import GIT_DIFF_IGNORE_WHITESPACE

from ellen.utils import JagareError
from ellen.utils.git import format_blob
from ellen.utils.git import format_tree
from ellen.utils.git import format_commit
from ellen.utils.git import format_tag
from ellen.utils.git import format_blame
from ellen.utils.git import format_diff
from ellen.utils.git import _resolve_version
from ellen.utils.git import _resolve_type
from ellen.utils.process import call, call2, _shlex_split
from ellen.tree import ls_tree
from ellen.rev_list import rev_list
from ellen.rename import detect_renamed
from ellen.tag import list_tags
from ellen.commit import create_commit
from ellen.diff import diff
from ellen.ref import update_ref
from ellen.clone import clone_repository
from ellen.clone import update_server_info
from ellen.init import init_repository
from ellen.archive import archive_repository


class Jagare(object):
    ''' pygit2 and git commands wrapper '''

    def __init__(self, path):
        self.repository = repository(path)
        self.repository_name = None

    @property
    def empty(self):
        return self.repository.is_empty

    @property
    def bare(self):
        return self.repository.is_bare

    @property
    def branches(self):
        return self.list_branches()

    @property
    def tags(self):
        return self.list_tags(name_only=True)

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
        if lineno:
            result = call(self.repository,
                          'blame -L %s,%s --porcelain %s -- %s' % (
                              lineno, lineno, ref, path))
        else:
            result = call(self.repository,
                          'blame -p -CM %s -- %s' % (ref, path))
        result = format_blame(result['stdout'], self.repository)
        return self.show(ref), result

    def format_patch(self, ref, from_ref=None):
        if from_ref:
            result = call(self.repository,
                          'format-patch --stdout %s...%s' % (from_ref, ref))
        else:
            result = call(self.repository, 'format-patch -1 --stdout %s' % ref)
        return result['stdout']

    def detect_renamed(self, ref, path=None):
        return detect_renamed(self.repository, ref)

    def commit_file(self, *w, **kw):
        return create_commit(self.repository, *w, **kw)

    def diff(self, *w, **kw):
        ''' Jagare's diff wrapper '''
        try:
            kws = {}
            ignore_space = kw.get('ignore_space', None)
            if ignore_space:
                flags = kw.get('flags', 0)
                flags |= GIT_DIFF_IGNORE_WHITESPACE
                kws.update({'flags': flags})
            from_ref = kw.get('from_ref', None)
            if from_ref:
                kws.update({'from_ref': from_ref})
            context_lines = kw.get('context_lines', None)
            if context_lines:
                kws.update({'context_lines': context_lines})
            path = kw.get('path', None)
            paths = kw.get('paths', None)
            if path:
                kws.update({'paths': [path]})
            if paths:
                kws.update({'paths': paths})
            # call diff
            d = diff(self.repository, *w, **kws)
            rename_detection = kw.get('rename_detection', None)
            if rename_detection:
                d['diff'].find_similar()
                #d.find_similar()
            # return formated diff dict
            return format_diff(d)
        except JagareError:
            return []

    def resolve_commit(self, version):
        version = version.strip()
        return _resolve_version(self.repository, version)

    def resolve_type(self, version):
        version = version.strip()
        return _resolve_type(self.repository, version)

    def clone(self, path, bare=None, branch=None, mirror=None, env=None):
        # TODO: check clone result
        clone_repository(self.repository.path, path,
                         bare=bare, checkout_branch=branch,
                         mirror=mirror, env=env)
        jagare = Jagare(path)
        if bare:
            update_server_info(jagare.repository)
        return jagare

    @classmethod
    def mirror(cls, url, path, bare=None, branch=None, env=None):
        # TODO: check clone result
        clone_repository(url, path,
                         bare=bare, checkout_branch=branch,
                         mirror=True, env=env)
        jagare = Jagare(path)
        if bare:
            update_server_info(jagare.repository)
        return jagare

    @classmethod
    def init(cls, path, work_path=None, bare=None):
        # TODO: move to libs
        # if parent dir not exist, create it.
        # else git init will fail
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

    def sha(self, rev='HEAD'):
        return _resolve_version(self.repository, rev)

    def merge_base(self, to_sha, from_sha):
        return self.repository.merge_base(to_sha, from_sha)

    # change to property ?
    def remotes(self):
        return self.repository.remotes

    def fetch_all(self):
        for remote in self.remotes():
            remote.fetch()

    def fetch(self, name):
        target = ''
        for remote in self.remotes():
            if remote.name == name:
                target = remote
        if target:
            target.fetch()

    def merge(self, ref, msg='automerge', commit_msg='',
              no_ff=False, _raise=True, _env=None):
        cmd = ['merge', ref]
        if msg:
            cmd.append('-m')
            cmd.append(msg)
        if commit_msg:
            cmd.append('-m')
            cmd.append(commit_msg)
        if no_ff:
            cmd.append('--no-ff')
        errcode = call(self.repository, cmd, env=_env)
        return errcode

    def push(self, remote, ref):
        cmd = ['push', remote, ref]
        errcode = call(self.repository, cmd)
        return errcode

    def archive(self, prefix):
        result = archive_repository(self.repository.path, prefix)
        return result['stdout']

    def delete_branch(self, name):
        branch = self.repository.lookup_branch(name)
        if branch:
            branch.delete()

    @property
    def head(self):
        if self.repository.is_empty:
            return None
        return self.repository.head

    def update_head(self, name):
        branch = self.repository.lookup_branch(name)
        if not branch:
            return None
        head = self.repository.lookup_reference("HEAD")
        if not head:
            return None
        head.target = branch.name


def repository(path):
    try:
        repo = Repository(path)
    except KeyError:
        raise JagareError('repo %s not exists' % path)
    return repo

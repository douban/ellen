#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from itertools import izip, count

from pygit2 import Repository
from pygit2 import GIT_OBJ_COMMIT

from ellen.utils import JagareError
from ellen.utils.format import format_obj
from ellen.utils.git import resolve_version
from ellen.utils.git import resolve_type
from ellen.git.tree import ls_tree
from ellen.git.rev_list import rev_list
from ellen.git.rename import detect_renamed
from ellen.git.tag import list_tags, create_tag
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
from ellen.git.fetch import fetch_repository
from ellen.utils.text import trunc_utf8

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
        """ return pygit2.Reference """
        # FIXME: return repo.head.name ?
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
    # FIXME: return [remote.name], and pygit2.remotes be internal
    def remotes(self):
        return self.repository.remotes

    def list_tags(self, *w, **kw):
        return list_tags(self.repository, *w, **kw)

    def list_branches(self):
        branches = self.repository.listall_branches()
        return branches

    def show(self, ref):
        """return formated dict"""
        try:
            obj = self.repository.revparse_single(ref)
        except KeyError:
            return {}
        return format_obj(obj, repository)

    def ls_tree(self, ref, path=None, recursive=False, size=None,
                with_commit=False, name_only=None):
        return ls_tree(self.repository, ref, req_path=path,
                       recursive=recursive, size=size,
                       with_commit=with_commit, name_only=name_only)

    def rev_list(self, *w, **kw):
        commits = []
        try:
            commits = rev_list(self.repository, *w, **kw)
        except KeyError:
            # FIXME: use JagareError
            pass
        return commits

    # FIXME: just return result
    def blame(self, ref, path):
        commit = self.repository.revparse_single(ref)
        oid = commit.oid
        result = blame(self.repository, path, oid)
        return result

    def format_blame_line(self, lineno, src_line, hunk):
        filename = hunk.orig_path
        sha = hunk.final_commit_id
        msg = self.repository[sha].message
        author = hunk.final_committer.name
        old_no = hunk.orig_start_line_number
        time = datetime.fromtimestamp(float(
            hunk.final_committer.time)).strftime('%Y-%m-%d')
        email = hunk.final_committer.email
        disp_filename = trunc_utf8(
            filename.encode('utf-8'), 20).decode('utf-8', 'ignore')
        disp_msg = trunc_utf8(
            msg.encode('utf-8'), 30).decode('utf-8', 'ignore')

        keys = ('sha', 'author', 'email', 'lineno', 'old_no',
                'filename', 'disp_filename', 'summary', 'disp_summary',
                'time', 'src_line')

        return dict(zip(keys, (sha, author, email, lineno, old_no,
                filename, disp_filename, msg, disp_msg,
                time, src_line)))

    def get_blame(self, ref, path, lineno=None):
        blame = self.blame(ref, path)
        blob = self.show("%s:%s" % (ref, path))
        if not blob:
            return None
        src = blob['data'].splitlines()
        if lineno:
            hunk = blame.for_line(lineno)
            src_line = src[int(lineno)-1]
            return self.format_blame_line(lineno,
                                          src_line, hunk)
        # format with raw_text
        else:
            result = []
            for idx, line in enumerate(src):
               lineno = idx + 1
               src_line = line
               hunk = blame.for_line(lineno)
               result.append(self.format_blame_line(
                   lineno, src_line, hunk))
        return result

    def format_patch(self, ref, from_ref=None):
        return format_patch(self.repository, ref, from_ref)

    # FIXME: path arg no use?
    def detect_renamed(self, ref, path=None):
        return detect_renamed(self.repository, ref)

    def commit_file(self, *w, **kw):
        return create_commit(self.repository, *w, **kw)

    def diff(self, *w, **kw):
        return diff(self.repository, *w, **kw)

    def resolve_commit(self, version):
        version = version.strip()
        return resolve_version(self.repository, version)

    def resolve_type(self, version):
        version = version.strip()
        return resolve_type(self.repository, version)

    def create_branch(self, name, ref, force=False):
        obj = self.repository.revparse_single(ref)
        if obj.type == GIT_OBJ_COMMIT:
            self.repository.create_branch(name, obj, force)
            return True
        else:
            return False

    def delete_branch(self, name):
        branch = self.repository.lookup_branch(name)
        if branch:
            branch.delete()

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
        # if parent dir not exist, create it.
        if not os.path.exists(path):
            os.makedirs(path)
        init_repository(path, work_path=work_path, bare=bare)
        return cls(path)

    # TODO: rename to list_references
    def listall_references(self):
        """return a list, e.g. ['refs/heads/master', ...]"""
        return self.repository.listall_references()

    # FIXME: 不要暴露出 pygit2.Reference 很难封装
    # TODO: 改成 internal 的
    def lookup_reference(self, name):
        return self.repository.lookup_reference(name)

    # TODO: 从 Code 移到 ellen
    # def get_latest_update_branches

    def add_remote(self, name, url):
        self.repository.create_remote(name, url)

    # FIXME: retval
    def update_ref(self, ref, newvalue):
        return update_ref(self.repository, ref, newvalue)

    # FIXME: retval
    def update_head(self, branch_name):
        branch = self.repository.lookup_branch(branch_name)
        if not branch:
            return None
        self.update_ref('HEAD', branch.name)

    def sha(self, rev='HEAD'):
        return self.resolve_commit(rev)

    # FIXME: return pygit2.Oid.hex
    def merge_base(self, to_sha, from_sha):
        """return pygit2.Oid"""
        return self.repository.merge_base(to_sha, from_sha)

    def fetch_all(self):
        for remote in self.remotes():
            remote.fetch()

    def fetch(self, name):
        target = {remote.name: remote for remote in self.remotes()}.get(name)
        if target:
            target.fetch()

    def fetch_(self, **kw):
        return fetch_repository(self.repository, **kw)

    def merge(self, ref, msg='automerge', commit_msg='',
              no_ff=False, _raise=True, _env=None):
        return merge(self.repository, ref, msg, commit_msg,
                     no_ff, _raise, _env)

    def push(self, remote, ref, _env=None):
        return push(self.repository, remote, ref, _env=_env)

    def archive(self, prefix, ref='master'):
        result = archive_repository(self.repository.path, prefix, ref)
        return result['stdout']

    def create_tag(self, name, ref, author_name, author_email, message):
        return create_tag(self.repository, name, ref,
                          author_name, author_email, message)


def repository(path):
    try:
        repo = Repository(path)
    except KeyError:
        raise JagareError('repo %s not exists' % path)
    return repo

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile
from cStringIO import StringIO
from pygit2 import (GIT_FILEMODE_TREE as TREE,
                    GIT_FILEMODE_LINK as SYMLINK)
from ellen.utils.process import git_with_path


def archive_repository(path, prefix, ref='master'):
    """git archive command"""
    git = git_with_path(git_dir=path)

    # FIXME: why + '/' ?
    return git.archive(ref, prefix=prefix + '/')


def archive_repository2(repository, prefix, ref='master'):
    def _add_file(tar, entry, path=None):
        object = repo[entry.id].read_raw()
        name = path if path is not None else entry.name
        info = tarfile.TarInfo(name)
        info.size = len(object)
        info.mtime = timestamp
        info.uname = info.gname = 'root'  # For compatability with git
        if entry.filemode == SYMLINK:
            info.type = tarfile.SYMTYPE
            info.linkname = object
            info.mode = 0777

        tar.addfile(info, StringIO(object))

    def _add_dir(tar, tentry, path=[]):
        tree = repo[tentry.oid]
        path.append(tentry.name)
        for entry in tree:
            if entry.filemode == TREE:
                _add_dir(out, entry, path)
            else:
                path.append(entry.name)
                _add_file(out, entry, "/".join(path))

    repo = repository
    # FIXME: This assumes a ref pointing to a commit
    oid = repo.lookup_reference(ref).resolve().target
    commit = repo[oid]
    timestamp = commit.committer.time
    tree = commit.tree
    outbuffer = StringIO()
    out = tarfile.open(mode='w', fileobj=outbuffer)
    for entry in tree:
        if entry.filemode == TREE:
            _add_dir(out, entry)
        else:
            _add_file(out, entry)
    out.close()
    return outbuffer.getvalue()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo
from ellen.utils.format import (format_blame,
                                format_blame_hunk,
                                format_blob,
                                is_blob_binary)
from pygit2 import (GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES,
                    GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES)


def blame_(repository, ref, path, lineno=None):
    """ git blame """
    git = git_with_repo(repository)
    if lineno:
        cmdstr = ('-L %s,%s --porcelain %s -- %s'
                  % (lineno, lineno, ref, path))  # start == end
    else:
        cmdstr = '-p -CM %s -- %s' % (ref, path)
    ret = git.blame.call(cmdstr)
    result = format_blame(ret['stdout'], repository)
    return result


"""
/** Normal blame, the default */
GIT_BLAME_NORMAL = 0,

/** Track lines that have moved within a file (like `git blame -M`).
  * NOT IMPLEMENTED. */
GIT_BLAME_TRACK_COPIES_SAME_FILE = (1<<0),

/** Track lines that have moved across files in the same commit (like `git blame -C`).
  * NOT IMPLEMENTED. */
GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES = (1<<1),

/** Track lines that have been copied from another file that exists in the
  * same commit (like `git blame -CC`). Implies SAME_FILE.
  * NOT IMPLEMENTED. */
GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES = (1<<2),

/** Track lines that have been copied from another file that exists in *any*
  * commit (like `git blame -CCC`). Implies SAME_COMMIT_COPIES.
  * NOT IMPLEMENTED. */
GIT_BLAME_TRACK_COPIES_ANY_COMMIT_COPIES = (1<<3),
"""


def blame(repository, ref, path, lineno, **kw):
    """ pygit2 blame """
    blob = repository.revparse_single("%s:%s" % (ref, path))
    if not blob or is_blob_binary(blob):
        return None
    lines = blob.data.splitlines()
    if lineno:
        if lineno <= 0 and lineno > len(lines):
            return None

    flags = (GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES
             | GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES)
    commit = repository.revparse_single(ref)
    if not commit:
        return None
    newest_commit = commit.id
    blame = repository.blame(path, flags, newest_commit=newest_commit, **kw)
    if not blame:
        return None

    hunks = []
    if lineno:
        hunk = blame.for_line(lineno)
        hunks.append(format_blame_hunk(hunk,
                                       repository))
    else:
        # FIXME: if line in blame hunk, It should not be blamed again.
        for hunk in blame:
            hunks.append(format_blame_hunk(hunk,
                                           repository))
    result = {'blob': format_blob(blob, repository),
              'hunks': hunks}
    return result

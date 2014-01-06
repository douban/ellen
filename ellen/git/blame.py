#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo
from ellen.utils.format import format_blame
from pygit2 import (GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES,
    GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES)

def blame_(repository, ref, path, lineno=None):
    git = git_with_repo(repository)
    if lineno:
        cmdstr = ('-L %s,%s --porcelain %s -- %s'
                  % (lineno, lineno, ref, path))  # start == end
    else:
        cmdstr = '-p -CM %s -- %s' % (ref, path)
    ret = git.blame.call(cmdstr)
    result = format_blame(ret['stdout'], repository)
    return result

def blame(repository, file_path, newest_commit,
          oldest_commit=None, min_line=None, max_line=None):
    flags = GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES | GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES
    kwargs = {
        'newest_commit': newest_commit
    }

    if oldest_commit:
        kwargs.update({'oldest_commit': oldest_commit})
    if min_line and max_line:
        kwargs.update({
            'min_line': min_line,
            'max_line': max_line
        })
    result = repository.blame(file_path, flags, **kwargs)
    return result

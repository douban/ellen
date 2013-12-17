#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo
from ellen.utils.git import format_blame


def blame(repository, ref, path, lineno=None):
    git = git_with_repo(repository)
    if lineno:
        cmdstr = ('-L %s,%s --porcelain %s -- %s'
                  % (lineno, lineno, ref, path))  # start == end
    else:
        cmdstr = '-p -CM %s -- %s' % (ref, path)
    ret = git.blame.call(cmdstr)
    result = format_blame(ret['stdout'], repository)
    return result

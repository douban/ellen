#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo

def gc_repository(repository, aggressive=None, auto=None, quiet=None, 
                  prune=None):
    """git gc command
    """
    git = git_with_repo(repository)
    return git.gc(aggressive=aggressive, auto=auto, quiet=quiet, 
                  prune=prune)

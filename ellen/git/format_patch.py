#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_repo


def format_patch(repository, ref, from_ref=None):
    git = git_with_repo(repository)
    rev_range = '%s...%s' % (from_ref, ref) if from_ref else ref
    git_format_patch = git.bake('format-patch', stdout=True)
    if not from_ref:
        git_format_patch = git_format_patch.bake('-1')
    ret = git_format_patch(rev_range)
    return ret['stdout']

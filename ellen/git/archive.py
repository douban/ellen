#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git_with_path


def archive_repository(path, prefix, ref='master'):
    """git archive command"""
    git = git_with_path(git_dir=path)

    # FIXME: why + '/' ?
    return git.archive(ref, prefix=prefix + '/')

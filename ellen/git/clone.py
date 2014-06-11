#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import git, git_with_repo


def clone_repository(url, path, bare=None, checkout_branch=None, mirror=None,
                     env=None, shared=None):
    """git clone command
    NOTE: 因为`git clone`在本机上直接做硬链接,速度比pygit2.clone_repository快
    """
    return git.clone(url, path,
                     b=checkout_branch,
                     bare=bare,
                     mirror=mirror,
                     env=env,
                     shared=shared)


def update_server_info(repository):
    git = git_with_repo(repository)
    git('update-server-info')

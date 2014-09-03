# -*- coding: utf-8 -*-

from ellen.process import git, git_with_repo


def clone(url, path,
          bare=None,
          checkout_branch=None,
          mirror=None,
          env=None,
          shared=None):
    return git.clone(url, path,
                     b=checkout_branch,
                     bare=bare,
                     mirror=mirror,
                     env=env,
                     shared=shared)


def update_server_info(repository):
    git = git_with_repo(repository)
    git('update-server-info')

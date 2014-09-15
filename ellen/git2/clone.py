# -*- coding: utf-8 -*-

from ellen.process import git, git_with_repo


def clone(url, path,
          bare=None,
          branch=None,
          mirror=None,
          env=None,
          shared=None):
    return git.clone(url, path,
                     b=branch,
                     bare=bare,
                     mirror=mirror,
                     env=env,
                     shared=shared)


def clone_to(repository, path,
             bare=None,
             branch=None,
             mirror=None,
             env=None,
             shared=None):
    return git.clone(repository.path, path,
                     b=branch,
                     bare=bare,
                     env=env,
                     mirror=mirror,
                     shared=shared)


def update_server_info(repository):
    git = git_with_repo(repository)
    git('update-server-info')

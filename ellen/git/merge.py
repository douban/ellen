#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import call


def merge(repository, ref, msg='automerge', commit_msg='',
          no_ff=False, _raise=True, _env=None):
    cmd = ['merge', ref]
    if msg:
        cmd.append('-m')
        cmd.append(msg)
    if commit_msg:
        cmd.append('-m')
        cmd.append(commit_msg)
    if no_ff:
        cmd.append('--no-ff')
    errcode = call(repository, cmd, env=_env)
    return errcode

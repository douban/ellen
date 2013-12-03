#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import call


def push(repository, remote, ref):
    cmd = ['push', remote, ref]
    errcode = call(repository, cmd)
    return errcode

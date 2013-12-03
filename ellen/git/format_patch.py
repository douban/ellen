#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import call


def format_patch(repository, ref, from_ref=None):
    if from_ref:
        result = call(repository,
                      'format-patch --stdout %s...%s' % (from_ref, ref))
    else:
        result = call(repository, 'format-patch -1 --stdout %s' % ref)
    return result['stdout']

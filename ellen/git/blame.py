#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ellen.utils.process import call
from ellen.utils.git import format_blame


def blame(repository, ref, path, lineno=None):
    if lineno:
        result = call(repository,
                      'blame -L %s,%s --porcelain %s -- %s'
                      % (lineno, lineno, ref, path))
    else:
        result = call(repository,
                      'blame -p -CM %s -- %s' % (ref, path))
    result = format_blame(result['stdout'], repository)
    return result

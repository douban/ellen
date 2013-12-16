# -*- coding: utf-8 -*-

import os
import shutil


def copytree(src, dst, symlinks=False, ignore=None):
    """The destination directory, named by dst, can already exist,
    see http://docs.python.org/2/library/shutil.html#shutil.copytree"""
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

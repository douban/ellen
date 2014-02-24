#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil


def update_hooks(repository, path):
    current_path = os.path.join(repository.path, 'hooks')
    if os.path.exists(current_path):
        if os.path.islink(current_path):
            os.unlink(current_path)
        elif os.path.isdir(current_path):
            shutil.rmtree(current_path)
        else:
            os.unlink(current_path)
    os.symlink(path, current_path)

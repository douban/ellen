# -*- coding: utf-8 -*-

import os
from _base import BareRepoTest
from ellen.repo import Jagare
from ellen.git.hook import update_hooks


class TestHook(BareRepoTest):

    def test_update(self):
        repo = Jagare(self.path)
        path = os.path.join(self.path, 'hooks')
        assert os.path.islink(path) is False
        target = '/'
        update_hooks(repo.repository, target)
        assert os.path.islink(path) is True
        assert os.path.realpath(path) == target

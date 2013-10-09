# -*- coding: utf-8 -*-

from _base import BareRepoTest
from ellen.repo import Jagare


class test_diff(BareRepoTest):

    def test_diff_text(self):
        repo = Jagare(self.path)

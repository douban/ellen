# -*- coding: utf-8 -*-

from _base import BareRepoTest
from ellen.repo import Jagare


# TODO:

class TestDiff(BareRepoTest):

    def test_diff_text(self):
        repo = Jagare(self.path)

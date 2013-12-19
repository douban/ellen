# -*- coding: utf-8 -*-

from _base import BareRepoTest
from _base import BARE_REPO_TAGS
from ellen.repo import Jagare


class TestTag(BareRepoTest):

    def test_simple(self):
        repo = Jagare(self.path)
        tags = repo.tags
        assert tags == BARE_REPO_TAGS

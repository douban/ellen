# -*- coding: utf-8 -*-

from _base import BareRepoTest
from _base import BARE_REPO_TAGS
from ellen.repo import Jagare


class test_tag(BareRepoTest):

    def test_simple(self):
        repo = Jagare(self.path)
        tags = repo.tags
        assert tags == BARE_REPO_TAGS

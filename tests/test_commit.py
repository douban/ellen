# -*- coding: utf-8 -*-

from _base import BareRepoTest
from ellen.repo import Jagare


class TestCommit(BareRepoTest):

    def test_resolve_commit(self):
        repo = Jagare(self.path)
        test_commit_hex1 = 'e9f35005ca7d004d87732598f761b1be3b9d1c61'
        test_commit_tree_hex1 = 'be483ca0381e9a61b76fac84863acdd970b9150f'
        test_commit_blob_hex1 = '7a8a76c619b95af88fb71e5514509e9ac8da6779'
        test_master_commit_hex = '9119237c2d5aa2c4a110296e255c7ec194711066'
        # FIXME tag test
        assert repo.resolve_commit(test_commit_hex1) == test_commit_hex1
        assert repo.resolve_commit(test_commit_tree_hex1) is None
        assert repo.resolve_commit(test_commit_blob_hex1) is None
        assert repo.resolve_commit('master') == test_master_commit_hex

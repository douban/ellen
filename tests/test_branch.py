# -*- coding: utf-8 -*-

from _base import BareRepoTest
from _base import BARE_REPO_BRANCHES
from ellen.repo import Jagare


class test_branch(BareRepoTest):

    def test_simple(self):
        repo = Jagare(self.path)
        branches = repo.branches
        assert branches == BARE_REPO_BRANCHES

    def test_delete(self):
        repo = Jagare(self.path)
        path = self.get_temp_path()
        clone_repo = repo.clone(path, bare=True)
        clone_repo.delete_branch('chinese')
        branches = clone_repo.branches
        assert 'chinese' in repo.branches
        assert 'chinese' not in branches
        assert 'master' in branches

# -*- coding: utf-8 -*-

from pygit2 import Repository
from pygit2 import is_repository
from _base import NoneRepoTest
from ellen.repo import Jagare


class TestInit(NoneRepoTest):

    def test_empty(self):
        self.clean()
        repo = Jagare.init(self.path, work_path=self.path)  # git_dir == work_tree ??
        pygit2_repo = Repository(self.path)
        assert is_repository(self.path) is True
        assert repo.empty is True
        assert repo.bare is False
        assert pygit2_repo.is_empty is True
        assert pygit2_repo.is_bare is False

    def test_bare(self):
        self.clean()
        repo = Jagare.init(self.path, bare=True)
        pygit2_repo = Repository(self.path)
        assert is_repository(self.path) is True
        assert repo.empty is True
        assert repo.bare is True
        assert pygit2_repo.is_empty is True
        assert pygit2_repo.is_bare is True

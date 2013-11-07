# -*- coding: utf-8 -*-

from pygit2 import Repository
from pygit2 import is_repository
from _base import BareRepoTest
from ellen.repo import Jagare


class test_clone(BareRepoTest):

    def test_simple(self):
        repo = Jagare(self.path)
        path = self.get_temp_path()
        clone_repo = repo.clone(path)
        pygit2_repo = Repository(path)
        assert is_repository(path) is True
        assert pygit2_repo.is_empty is False
        assert pygit2_repo.is_bare is False
        assert clone_repo.empty is False
        assert clone_repo.bare is False

    def test_bare(self):
        repo = Jagare(self.path)
        path = self.get_temp_path()
        clone_repo = repo.clone(path, bare=True)
        pygit2_repo = Repository(path)
        assert is_repository(path) is True
        assert pygit2_repo.is_empty is False
        assert pygit2_repo.is_bare is True
        assert clone_repo.empty is False
        assert clone_repo.bare is True

    def test_mirror(self):
        repo = Jagare(self.path)
        path = self.get_temp_path()
        clone_repo = repo.clone(path, mirror=True)
        pygit2_repo = Repository(path)
        assert is_repository(path) is True
        assert pygit2_repo.is_empty is False
        assert pygit2_repo.is_bare is True
        assert clone_repo.empty is False
        assert clone_repo.bare is True

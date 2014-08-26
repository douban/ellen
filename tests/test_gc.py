# -*- coding: utf-8 -*-

from pygit2 import Repository
from pygit2 import is_repository
from _base import BareRepoTest
from ellen.repo import Jagare

class test_gc(BareRepoTest):

    def test_simple(self):
        repo = Jagare(self.path)
        pygit2_repo = Repository(self.path)
        ret = repo.gc()
        self.assertEqual(ret['returncode'], 0)
        self.assertTrue('gc' in ret['fullcmd'])
        self.assertFalse(pygit2_repo.is_empty)
        self.assertTrue(pygit2_repo.is_bare)
        self.assertFalse(repo.empty)
        self.assertTrue(repo.bare)

    def test_simple_auto(self):
        repo = Jagare(self.path)
        pygit2_repo = Repository(self.path)
        ret = repo.gc(auto=True)
        self.assertEqual(ret['returncode'], 0)
        self.assertTrue('gc' in ret['fullcmd'])
        self.assertFalse(pygit2_repo.is_empty)
        self.assertTrue(pygit2_repo.is_bare)
        self.assertFalse(repo.empty)
        self.assertTrue(repo.bare)

    def test_simple_all(self):
        repo = Jagare(self.path)
        pygit2_repo = Repository(self.path)
        ret = repo.gc(prune='all')
        self.assertEqual(ret['returncode'], 0)
        self.assertTrue('gc' in ret['fullcmd'])
        self.assertFalse(pygit2_repo.is_empty)
        self.assertTrue(pygit2_repo.is_bare)
        self.assertFalse(repo.empty)
        self.assertTrue(repo.bare)

    def test_multi(self):
        repo = Jagare(self.path)
        path = self.get_temp_path()
        clone_repo = repo.clone(path, shared=True)
        pygit2_repo = Repository(path)
        ret = repo.gc(fork_paths=path)
        self.assertTrue(is_repository(path))
        self.assertFalse(pygit2_repo.is_empty)
        self.assertFalse(pygit2_repo.is_bare)
        self.assertFalse(clone_repo.empty)
        self.assertFalse(clone_repo.bare)

    def test_multi_auto(self):
        repo = Jagare(self.path)
        path = self.get_temp_path()
        clone_repo = repo.clone(path, shared=True)
        pygit2_repo = Repository(path)
        ret = repo.gc(fork_paths=path, auto=True)
        self.assertTrue(is_repository(path))
        self.assertFalse(pygit2_repo.is_empty)
        self.assertFalse(pygit2_repo.is_bare)
        self.assertFalse(clone_repo.empty)
        self.assertFalse(clone_repo.bare)

    def test_multi_all(self):
        repo = Jagare(self.path)
        path = self.get_temp_path()
        clone_repo = repo.clone(path, shared=True)
        pygit2_repo = Repository(path)
        ret = repo.gc(fork_paths=path, auto=True)
        self.assertTrue(is_repository(path))
        self.assertFalse(pygit2_repo.is_empty)
        self.assertFalse(pygit2_repo.is_bare)
        self.assertFalse(clone_repo.empty)
        self.assertFalse(clone_repo.bare)

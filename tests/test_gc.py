# -*- coding: utf-8 -*-

import unittest
from pygit2 import Repository
from pygit2 import is_repository
from _base import BareRepoTest
from ellen.repo import Jagare
from ellen.git.gc import BfsQue

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


class Node(object):
    def __init__(self, id, parents):
        self.id = id
        self.parents = parents


class test_que(unittest.TestCase):
    def setUp(self):
        self.node7 = Node(7, [])
        self.node5, self.node6 = Node(5, [self.node7]), Node(6, [self.node7])
        self.node3, self.node4 = Node(3, [self.node5]), Node(4, [self.node6])
        self.node2 = Node(2, [self.node3, self.node4])
        self.node1 = Node(1, [self.node2])
        self.first_node = Node(0, [self.node1])
        self.cnd_fn = lambda item, wanted: item in wanted

    def test_basic1(self):
        self.que = BfsQue([self.first_node], cnd_fn=self.cnd_fn)
        self.que.search(self.first_node)
        self.assertEqual(self.que.data, [self.first_node])

    def test_basic2(self):
        self.que = BfsQue([self.node1], cnd_fn=self.cnd_fn)
        self.que.search(self.first_node)
        self.assertEqual(self.que.data, [self.node1])

    def test_basic3(self):
        self.que = BfsQue([self.node3, self.node4], cnd_fn=self.cnd_fn)
        self.que.search(self.first_node)
        self.assertEqual(self.que.data, [self.node3, self.node4])

    def test_basic4(self):
        self.que = BfsQue([self.node5, self.node6], cnd_fn=self.cnd_fn)
        self.que.search(self.first_node)
        self.assertEqual(self.que.data, [self.node5, self.node6])

    def test_basic5(self):
        self.que = BfsQue([self.node7], cnd_fn=self.cnd_fn)
        self.que.search(self.first_node)
        self.assertEqual(self.que.data, [self.node7])

    def test_neg1(self):
        self.que = BfsQue([self.node3], cnd_fn=self.cnd_fn)
        self.que.search(self.first_node)
        self.assertEqual(self.que.data, [self.node3])

    def test_neg2(self):
        self.que = BfsQue([self.node5], cnd_fn=self.cnd_fn)
        self.que.search(self.first_node)
        self.assertEqual(self.que.data, [self.node5])
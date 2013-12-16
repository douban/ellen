# -*- coding: utf-8 -*-

from _base import BareRepoTest
from ellen.repo import Jagare


class TestPush(BareRepoTest):

    def test_push(self):
        repo = Jagare(self.path)

        path2 = self.get_temp_path()
        repo2 = Jagare.init(path2, bare=True)
        assert repo2.empty

        repo.add_remote('origin', repo2.path)
        repo.push('origin', 'master')
        assert not repo2.empty

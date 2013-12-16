# -*- coding: utf-8 -*-

from _base import BareRepoTest

from ellen.repo import Jagare


class TestBlame(BareRepoTest):
    def test_blame(self):
        repo = Jagare(self.path)

        tree = repo.ls_tree('master')
        blobs = [item['path'] for item in tree if item['type'] == 'blob']
        for node in blobs:
            obj_dict, blame_ret = repo.blame('master', path=node)
            assert type(obj_dict) is dict
            assert blame_ret

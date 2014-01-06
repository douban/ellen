# -*- coding: utf-8 -*-

from _base import BareRepoTest
from ellen.repo import Jagare


class TestBlame(BareRepoTest):
    def test_blame(self):
        repo = Jagare(self.path)

        tree = repo.ls_tree('master')
        blobs = [item['path'] for item in tree if item['type'] == 'blob']
        for node in blobs:
            blame_ret = repo.blame('master', path=node)
            if node == 'new.txt':
                for hunk in blame_ret:
                    self.assertEquals('4bc90207e76d68d5cda435e67c5f85a0ce710f44',
                                      hunk.final_commit_id)
                    self.assertEquals(hunk.final_committer.email, 'xutao@douban.com')
            if node == 'README.md':
                for hunk in blame_ret:
                    self.assertEquals('e9f35005ca7d004d87732598f761b1be3b9d1c61',
                                      hunk.final_commit_id)
                    self.assertEquals(hunk.final_committer.email, 'xutao@douban.com')

# -*- coding: utf-8 -*-

import os

from _base import BareRepoTest, BARE_REPO_OTHER_BRANCH

from ellen.repo import Jagare
from ellen.utils.temp_repo import commit_something


class TestMerge(BareRepoTest):

    def _merge(self, no_ff):
        repo = Jagare(self.path)
        BR = 'br_test_merge'
        path = self.get_temp_path()

        # repo has work-tree
        repo.clone(path, branch=BARE_REPO_OTHER_BRANCH)
        repo = Jagare(os.path.join(path, '.git'))

        ret = repo.create_branch(BR, BARE_REPO_OTHER_BRANCH)
        assert ret
        sha1 = repo.sha(BARE_REPO_OTHER_BRANCH)

        commit_something(path, branch=BR)
        repo.update_head(BARE_REPO_OTHER_BRANCH)
        ret = repo.merge(BR, no_ff=no_ff)
        sha2 = repo.sha(BARE_REPO_OTHER_BRANCH)

        assert sha1 != sha2
        assert repo.sha(sha1) == sha1

    def test_merge(self):
        self._merge(no_ff=False)

    def test_merge_no_ff(self):
        self._merge(no_ff=True)

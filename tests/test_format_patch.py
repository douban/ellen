# -*- coding: utf-8 -*-

from _base import BareRepoTest, BARE_REPO_OTHER_BRANCH

from ellen.repo import Jagare


class TestFormatPatch(BareRepoTest):
    def test_format_patch(self):
        repo = Jagare(self.path)

        ret = repo.format_patch('master')
        assert ret

        ret = repo.format_patch(BARE_REPO_OTHER_BRANCH, from_ref='master')
        assert ret

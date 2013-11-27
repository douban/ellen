# coding: utf-8

from ellen.repo import Jagare
from ellen.utils.temp_repo import create_temp_repo
from _base import RepoTest


class TestUtils(RepoTest):

    def test_create_temp_repo(self):
        tempdir = self.get_temp_path()
        repo = create_temp_repo(tempdir, is_bare=True)
        assert repo

        repo2 = Jagare(tempdir)
        assert repo == repo2
        assert repo2.bare is True
        assert repo2.empty is False

 # -*- coding: utf-8 -*-

import os
import shutil
import tempfile
from pygit2 import init_repository
from pygit2 import Repository

UNINIT_REPO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "initRepo")
BARE_REPO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "bare_repo1")
BARE_REPO_BRANCH = ('chinese', 'master')
BARE_REPO_TAG = ()


class TempTest(object):

    def init_temp_path(self):
        self.temp_paths = []

    def get_temp_path(self):
        path = tempfile.mkdtemp()
        self.temp_paths.append(path)
        return path

    def clean_temp_path(self):
        for path in self.temp_paths:
            shutil.rmtree(path)


class RepoTest(TempTest):

    def setUp(self):
        self.init_temp_path()

    def tearDown(self):
        self.clean_temp_path()


class NoneRepoTest(TempTest):

    def setUp(self):
        self.init_temp_path()
        self.path = UNINIT_REPO_PATH
        shutil.rmtree(self.path, ignore_errors=True)

    def tearDown(self):
        self.clean_temp_path()
        shutil.rmtree(self.path, ignore_errors=True)

    def clean(self):
        shutil.rmtree(self.path, ignore_errors=True)


class BareRepoTest(TempTest):

    def setUp(self):
        self.init_temp_path()
        self.path = BARE_REPO_PATH

    def tearDown(self):
        self.clean_temp_path()


class EmptyRepoTest(RepoTest):

    def setUp(self):
        self.init_temp_path()

    def tearDown(self):
        self.clean_temp_path()

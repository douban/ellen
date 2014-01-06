# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import tempfile
from utils import copytree

UNINIT_REPO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "initRepo")
BARE_REPO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "bare_repo1")
BARE_REPO_OTHER_BRANCH = 'chinese'
BARE_REPO_BRANCHES = [BARE_REPO_OTHER_BRANCH, 'master']
BARE_REPO_TAGS = ('tag1',)


class TempTest(unittest.TestCase):

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


# TODO: add self.repo ?
class BareRepoTest(TempTest):

    def setUp(self):
        self.init_temp_path()
        self.path = self.get_temp_path()
        copytree(BARE_REPO_PATH, self.path)

    def tearDown(self):
        self.clean_temp_path()


class EmptyRepoTest(RepoTest):

    def setUp(self):
        self.init_temp_path()

    def tearDown(self):
        self.clean_temp_path()

# -*- coding: utf-8 -*-

import os

from ellen.repo import Jagare


def create_temp_repo(path, is_bare=True):
    repo = Jagare.init(path, bare=is_bare)

    data = [(os.path.join(path, 'test_file'),
             """test_content
             test_content
             test_content
             """,
             'insert')]

    repo.commit_file(branch='master',
                     parent='master',
                     author_name='testuser',
                     author_email='testuser@xxx.com',
                     message='first commit',
                     reflog='commit one file',
                     data=data)

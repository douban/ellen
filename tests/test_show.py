# -*- coding: utf-8 -*-

from _base import BareRepoTest, BARE_REPO_TAGS

from ellen.repo import Jagare


class TestShow(BareRepoTest):

    def test_show_commit(self):
        repo = Jagare(self.path)
        ret = repo.show('master')
        assert ret

    def test_show_tree(self):
        repo = Jagare(self.path)
        ls = repo.ls_tree('master')
        trees = [item['sha'] for item in ls if item['type'] == 'tree']
        for sha in trees:
            ret = repo.show(sha)
            assert ret['type'] == 'tree'

    def test_show_blob(self):
        repo = Jagare(self.path)
        ls = repo.ls_tree('master')
        blobs = [item['sha'] for item in ls if item['type'] == 'blob']
        for sha in blobs:
            ret = repo.show(sha)
            assert ret['type'] == 'blob'

    def test_show_tag(self):
        repo = Jagare(self.path)
        tag_name = repo.tags[0]
        tag_ref = repo.lookup_reference('refs/tags/%s' % tag_name)
        sha = tag_ref.target.hex

        type_ = repo.resolve_type(sha)
        assert type_ == 'tag'

        ret = repo.show(sha)
        assert ret['name'] == BARE_REPO_TAGS[0]

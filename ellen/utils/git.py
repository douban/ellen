#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
git
---

.. autofunction:: endwith_git

.. autofunction:: format_pygit2_signature

.. autofunction:: _resolve_version
'''

from __future__ import absolute_import

import magic
from datetime import datetime
import re

from pygit2 import Repository
from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_BLOB
from pygit2 import GIT_OBJ_TREE
from pygit2 import GIT_OBJ_COMMIT

# from .text import highlight_code # no use yet
from .text import trunc_utf8
from . import JagareError
from .mdiff import mdiff2


PYGIT2_OBJ_TYPE = {
    GIT_OBJ_COMMIT: 'commit',
    GIT_OBJ_BLOB: 'blob',
    GIT_OBJ_TREE: 'tree',
    GIT_OBJ_TAG: 'tag',
}


def endwith_git(path):
    """给不以 .git 结尾的路径添加 .git 后缀。"""
    if not path.endswith(".git"):
        path = path + ".git"
    return path


def format_pygit2_signature(signature):
    # copy from http://code.dapps.douban.com/code/blob/f37dbf0a51a783fa3af14574a4379dd6e2d64b35/libs/git2.py#L-25
    '''格式化 pygit2 操作人信息'''
    d = {}
    d['date'] = datetime.fromtimestamp(
        signature.time,
        # FIXME: add offset for app.
        # FixedOffset(signature.offset, None)
    )
    d['name'] = signature.name
    d['email'] = signature.email
    # strftime('%Y-%m-%dT%H:%M:%S+0800')
    d['ts'] = str(signature.time)
    #d['tz'] = datetime.fromtimestamp(signature.time, FixedOffset(signature.offset, None)).strftime('%z')
    return d


def _resolve_version(repository, version):
    '''返回完整的 40 位的 commit hash '''
    try:
        obj = repository.revparse_single(version)
        if obj.type == GIT_OBJ_TAG:
            commit = repository[obj.target]
        elif obj.type == GIT_OBJ_COMMIT:
            commit = obj
        elif obj.type == GIT_OBJ_BLOB:
            return None
        elif obj.type == GIT_OBJ_TREE:
            return None
    except KeyError:
        return None
    return commit.hex


def _resolve_type(repository, version):
    try:
        obj = repository.revparse_single(version)
        if obj.type == GIT_OBJ_TAG:
            type = "tag"
        elif obj.type == GIT_OBJ_COMMIT:
            type = "commit"
        elif obj.type == GIT_OBJ_BLOB:
            type = "blob"
        elif obj.type == GIT_OBJ_TREE:
            type = "tree"
    except KeyError:
        type = None
    return type


def format_short_reference_name(name):
    short = ''
    if name.startswith('refs/heads/'):
        short = name[11:]
    elif name.startswith('refs/remotes/'):
        short = name[13:]
    elif name.startswith('refs/tags/'):
        short = name[10:]
    elif name.startswith('refs/'):
        short = name[5:]
    else:
        return name
    return short


def format_tag(ref, tag, repository):
    d = {}
    d['name'] = tag.name
    d['tag'] = tag.name
    d['target'] = tag.target.hex
    d['type'] = 'tag'
    d['tagger'] = format_pygit2_signature(tag.tagger)
    d['message'], _, d['body'] = tag.message.strip().partition('\n\n')
    d['sha'] = tag.hex
    return d


def format_lw_tag(ref, tag, repository):
    d = {}
    d['name'] = format_short_reference_name(ref)
    d['tag'] = d['name']
    d['object'] = tag.hex
    d['type'] = 'commit'
    d['commit'] = format_commit(ref, tag, repository)
    return d


def format_blob(sha, blob, repository):
    d = {}
    d['sha'] = blob.hex
    d['type'] = 'blob'
    d['data'] = blob.data
    d['size'] = blob.size
    d['binary'] = blob.binary and 'text' not in magic.from_buffer(blob.data, mime=True)
    return d


def format_tree(sha, tree, repository):
    d = {}
    d['type'] = 'tree'
    entries = []
    for entry in tree:
        mode = '%06o' % entry.filemode
        # FIXME: use pygit2 object
        if mode == '160000':
            objtype = 'commit'  # For git submodules
        elif mode == '040000':
            objtype = 'tree'
        else:
            objtype = 'blob'
        r = {
            'sha': entry.hex,
            'mode': mode,
            'type': objtype,
            'path': entry.name
        }
        entries.append(r)
    d['entries'] = entries
    return d


def format_commit(sha, commit, repository):
    d = {}
    # FIXME: parent or parents
    d['parent'] = [p.hex for p in commit.parents] if commit.parents else []
    d['parents'] = [p.hex for p in commit.parents] if commit.parents else []
    d['tree'] = commit.tree.hex
    d['committer'] = format_pygit2_signature(commit.committer)
    d['author'] = format_pygit2_signature(commit.author)
    d['email'] = commit.author.email  # FIXME
    d['time'] = d['author']['date']  # FIXME
    d['commit'] = commit.hex  # FIXME
    d['message'], _, d['body'] = commit.message.strip().partition('\n\n')
    d['sha'] = commit.hex
    return d


def format_blame(text, repository):
    RE_EMAIL = re.compile(r'<(?P<email>.*)>')
    # FIXME: highlight_code
    #def _blame_src_highlighted_lines(self, ref, path):
    #    HIGHLIGHT_PATN = re.compile(
    #        r'<a name="L-(\d+)"></a>(.*?)(?=<a name="L-(?:\d+)">)', re.DOTALL)
    #    source_code = repository.show('%s:%s' % (ref, path))
    #    source_code = source_code['data']
    #    # TODO try to avoid having highlighted content here
    #    hl_source_code = highlight_code(path, source_code)
    #    hl_lines = dict(re.findall(HIGHLIGHT_PATN, hl_source_code))
    #    return hl_lines
    res = text
    res = res.splitlines()
    #hl_lines = _blame_src_highlighted_lines(ref, path)
    hl_lines = {}
    blame = []
    rev_data = {}
    new_block = True
    for line in res:
        if new_block:
            sha, old_no, line_no = line.split()[:3]
            if sha not in rev_data:
                rev_data[sha] = {}
            rev_data[sha]['line_no'] = line_no
            rev_data[sha]['old_no'] = old_no
            new_block = False
        elif line.startswith('author '):
            _, _, author = line.partition(' ')
            rev_data[sha]['author'] = author.strip()
        elif line.startswith('author-time '):
            _, _, time = line.partition(' ')
            time = datetime.fromtimestamp(float(time)).strftime('%Y-%m-%d')
            rev_data[sha]['time'] = time
        elif line.startswith('author-mail '):
            _, _, email = line.partition(' ')
            email = RE_EMAIL.match(email).group('email')
            rev_data[sha]['email'] = email
        elif line.startswith('summary '):
            _, _, summary = line.partition(' ')
            rev_data[sha]['summary'] = summary.strip()
            disp_summary = trunc_utf8(
                summary.encode('utf-8'), 20).decode('utf-8', 'ignore')
            rev_data[sha]['disp_summary'] = disp_summary
        elif line.startswith('filename'):
            _, _, filename = line.partition(' ')
            rev_data[sha]['filename'] = filename
            filename = trunc_utf8(
                filename.strip().encode('utf-8'), 30).decode('utf-8', 'ignore')
            rev_data[sha]['disp_name'] = filename
        elif line.startswith('\t'):
            # Try to get an highlighted line of source code
            code_line = hl_lines.get(str(
                line_no), '').replace('\n', '').decode('utf-8', 'ignore')
            if not code_line:
                code_line = line[1:]
            blame.append((
                sha,
                rev_data[sha]['author'],
                rev_data[sha]['email'],
                rev_data[sha]['time'],
                rev_data[sha]['disp_summary'],
                rev_data[sha]['summary'],
                rev_data[sha]['line_no'],
                rev_data[sha]['old_no'],
                rev_data[sha]['filename'],
                rev_data[sha]['disp_name'],
                code_line,
            ))
            new_block = True
    return blame


def format_diff(diff):
    ''' format diff into a dict '''
    _patches = []
    patches = diff['diff']
    old_sha = diff['old_sha']
    new_sha = diff['new_sha']
    for patch in patches:
        _patches.append({
            'amode': '100644',
            'bmode': '100644',
            'asha': patch.old_oid,  # no use? same with 'old_oid'
            'bsha': patch.new_oid,
            'old_sha': old_sha,
            'new_sha': new_sha,
            'change': patch.status,
            'filename': patch.old_file_path,
            'new_filename': patch.new_file_path,
            'additions': patch.additions,
            'deletions': patch.deletions,
            'similarity': patch.similarity,
            'hunks': _format_hunks(patch.hunks),
            'old_oid': patch.old_oid,
            'new_oid': patch.new_oid,
            'status': patch.status,
            'binary': patch.binary,
            'old_file_path': patch.old_file_path,
            'new_file_path': patch.new_file_path,
        })
    diff['patches'] = _patches
    return diff


# TODO: lines and mdiff
def _format_hunks(hunks):
    _hunks = []
    for hunk in hunks:
        wrapped_hunk = {
            'old_start': hunk.old_start,
            'new_start': hunk.new_start,
            'old_lines': hunk.old_lines,
            'new_lines': hunk.new_lines,
            'lines': hunk.lines,
            'mdiff': mdiff2(hunk.lines),
            }
        _hunks.append(wrapped_hunk)
    return _hunks


class GitRepository(Repository):

    def revparse_single(self, *w, **kw):
        try:
            return super(GitRepository, self).revparse_single(*w, **kw)
        except (KeyError, ValueError):
            raise JagareError("rev not found.", 400)

    def lookup_reference(self, *w, **kw):
        try:
            return super(GitRepository, self).lookup_reference(*w, **kw)
        except ValueError:
            raise JagareError("reference not found.", 400)

    def read(self, *w, **kw):
        try:
            return super(GitRepository, self).read(*w, **kw)
        except ValueError:
            raise JagareError("sha not found", 400)

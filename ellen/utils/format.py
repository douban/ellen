#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
from datetime import datetime

import mime
import magic

from ellen.utils.git import PYGIT2_OBJ_TYPE

# from ellen.utils.text import highlight_code # no use yet
from ellen.utils.text import trunc_utf8

m = magic._get_magic_type(True)
magic.magic_setflags(m.cookie,
                     magic.MAGIC_NONE |
                     magic.MAGIC_NO_CHECK_COMPRESS |
                     magic.MAGIC_NO_CHECK_TAR |
                     magic.MAGIC_NO_CHECK_SOFT |
                     magic.MAGIC_NO_CHECK_APPTYPE |
                     magic.MAGIC_NO_CHECK_ELF |
                     magic.MAGIC_NO_CHECK_FORTRAN |
                     magic.MAGIC_NO_CHECK_TROFF |
                     magic.MAGIC_NO_CHECK_TOKENS |
                     magic.MAGIC_MIME)


def format_obj(obj, repository):
    func_name = 'format_' + PYGIT2_OBJ_TYPE[obj.type]
    this = sys.modules[__name__]
    formatter = getattr(this, func_name)
    return formatter(obj, repository)


def format_commit(commit, repository):
    d = {}
    d['type'] = 'commit'
    # FIXME: use parents
    try:
        d['parent'] = [str(p.id) for p in commit.parents] if commit.parents else []
        d['parents'] = [str(p.id) for p in commit.parents] if commit.parents else []
    except KeyError:
        # FIXME: pygit2 commit.parents
        d['parent'] = []
        d['parents'] = []
    d['tree'] = str(commit.tree.id)
    d['committer'] = _format_pygit2_signature(commit.committer)
    d['author'] = _format_pygit2_signature(commit.author)
    d['email'] = commit.author.email  # FIXME
    d['commit'] = str(commit.id)  # FIXME
    d['message'], _, d['body'] = commit.message.strip().partition('\n\n')
    d['sha'] = str(commit.id)
    return d


def format_tree(tree, repository):
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
            'sha': str(entry.id),
            'mode': mode,
            'type': objtype,
            'path': entry.name
        }
        entries.append(r)
    d['entries'] = entries
    return d


def format_blob(blob, repository):
    d = {}
    d['sha'] = str(blob.id)
    d['type'] = 'blob'
    d['data'] = blob.data
    d['size'] = blob.size
    d['binary'] = is_blob_binary(blob)
    return d


def format_tag(tag, repository):
    d = {}
    d['name'] = tag.name
    d['tag'] = tag.name
    d['target'] = str(tag.target)
    d['type'] = 'tag'
    d['tagger'] = _format_pygit2_signature(tag.tagger)
    d['message'], _, d['body'] = tag.message.strip().partition('\n\n')
    d['sha'] = str(tag.id)
    return d


def format_lw_tag(ref, tag, repository):
    """format lightweight tag"""
    d = {}
    d['name'] = _format_short_reference_name(ref)
    d['tag'] = d['name']
    d['object'] = str(tag.id)
    d['type'] = 'commit'  # really useful ?
    d['commit'] = format_commit(tag, repository)
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
            'old_sha': old_sha,
            'new_sha': new_sha,
            'additions': patch.additions,
            'deletions': patch.deletions,
            'similarity': patch.similarity,
            'hunks': _format_hunks(patch.hunks),
            'old_oid': patch.old_oid,
            'new_oid': patch.new_oid,
            'status': patch.status,
            'binary': patch.is_binary,
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
            }
        _hunks.append(wrapped_hunk)
    return _hunks


def _format_short_reference_name(name):
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


def _format_pygit2_signature(signature):
    # copy from http://code.dapps.douban.com/code/blob/f37dbf0a51a783fa3af14574a4379dd6e2d64b35/libs/git2.py#L-25
    '''格式化 pygit2 操作人信息'''
    d = {}
    d['name'] = signature.name
    d['email'] = signature.email
    d['time'] = signature.time
    d['offset'] = signature.offset
    return d


def _format_pygit2_reference(reference):
    d = {}
    return d


def format_pygit2_blame(blame):
    d = {}
    return d


def format_blame_hunk(hunk, repository):
    d = {}
    d['lines_in_hunk'] = hunk.lines_in_hunk
    d['final_commit_id'] = hunk.final_commit_id
    d['final_start_line_number'] = hunk.final_start_line_number
    d['final_committer'] = _format_pygit2_signature(hunk.final_committer)
    d['orig_commit_id'] = hunk.orig_commit_id
    d['orig_path'] = hunk.orig_path
    d['orig_start_line_number'] = hunk.orig_start_line_number
    d['orig_committer'] = _format_pygit2_signature(hunk.orig_committer)
    d['boundary'] = hunk.boundary
    return d


def format_merge_analysis(analysis):
    from pygit2 import GIT_MERGE_ANALYSIS_FASTFORWARD, GIT_MERGE_ANALYSIS_UP_TO_DATE
    d = {}
    d['is_uptodate'] = analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
    d['is_fastforward'] = analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
    return d


def format_index(merge_index):
    d = {}
    d['has_conflicts'] = merge_index.has_conflicts
    return d


def is_blob_binary(blob):
    is_binary = blob.is_binary
    if is_binary:
        content_type = magic.from_buffer(blob.data[:1024], mime=True)
        # FIXME: dirty hack for 'text/x-python'
        if content_type and content_type.startswith('text/'):
            is_binary = False
        else:
            plaintext = mime.Types[content_type] if content_type else None
            text = plaintext[0] if plaintext else None
            is_binary = text.is_binary if text else is_binary
    return is_binary

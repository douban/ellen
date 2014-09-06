# -*- coding: utf-8 -*-
import os
import re
import sys
from functools import wraps
from ellen.utils.process import git_with_repo

P_OBJ = re.compile(r"^[0-9a-f]{38}$")

AGGRESSIVE_WINDOW = 250
AUTO_THRESHOLD = 6700
AUTO_PACK_LIMIT = 50
EXPIRE = '2.weeks.ago'
_OPTS = {'repack_all': {}}


def check_status(f):
    @wraps(f)
    def wrapper(*a, **kw):
        fn = a[0]
        status = f(*a, **kw)
        if status['returncode'] != 0:
            raise RuntimeError("'%s' failed during git.multi_gc" % fn.__name__)
        return status
    return wrapper


@check_status
def git_process(fn, *a, **kw):
    return fn(*a, **kw)


def _update_repack_all_options(expire=EXPIRE):
    a = True if "now" == expire else None
    A = True if expire else None
    unpack_unreachable = expire if expire else None
    _OPTS['repack_all'] = dict(a=a, A=A, unpack_unreachable=unpack_unreachable)


def _too_many_loose_objects(repository):
    obj_dir = os.path.join(repository.path, "objects/")
    if AUTO_THRESHOLD <= 0:
        return False
    auto_thr = (AUTO_THRESHOLD + 255) // 256
    if not os.path.isdir(obj_dir):
        return False
    files = os.listdir(obj_dir)
    root = obj_dir
    if not files:
        return False
    for f in files:
        path = os.path.join(root, f)
        if os.path.isdir(path):
            root = path
            break
    cnt = 0
    for f in os.listdir(root):
        path = os.path.join(root, f)
        if os.path.isfile(path) and P_OBJ.search(f):
            cnt += 1
    if cnt > auto_thr:
        return True
    return False


def _too_many_packs(repository):
    if AUTO_PACK_LIMIT <= 0:
        return False
    path = os.path.join(repository.path, "objects/info/packs")
    if not os.path.isfile(path):
        return False
    with open(path, 'r') as f:
        lines = f.readlines()
        packs = len(lines) - 1
        if packs >= AUTO_PACK_LIMIT:
            return True
    return False


def need_to_gc(repository, expire=EXPIRE):
    if AUTO_THRESHOLD <= 0:
        return False
    if _too_many_packs(repository):
        _update_repack_all_options(expire=expire)
    elif not _too_many_loose_objects():
        return False
    return True


class BfsQue(object):
    def __init__(self, wanted, cnd_fn=lambda x, s: x in s):
        self.data = []
        self.visited = []
        self.wanted = wanted
        self.cnd = cnd_fn

    def _visit(self, item):
        addq = lambda q, x: q.append(x)
        if self.cnd(item, self.wanted) and item not in self.data:
            addq(self.data, item)
            return True
        addq(self.visited, item)
        return False

    def search(self, item):
        empty = lambda x: len(x) == 0
        addq = lambda q, x: q.append(x)
        delq = lambda x: x.pop(0)
        avail = []
        if self._visit(item):
            return
        addq(avail, item)
        while not empty(avail):
            c = delq(avail)
            for p in c.parents:
                if p in self.visited or self._visit(p):
                    continue
                addq(avail, p)


def gc_repository(repository, forks, auto=None, prune=None):
    """git gc command
    """
    expire = 'now' if prune == 'all' else prune
    if not expire:
        expire = EXPIRE

    git = git_with_repo(repository)
    status = {'returncode': 0, 'fullcmd': '%s multi-gc' % ' '.join(git.cmds), 'stderr': '', 'stdout': ''}
    try:
        prune_opts = []
        if prune:
            prune_opts.append("--prune=" + prune)
            status['fullcmd'] += ' ' + prune_opts[0]

        if not forks:
            return git.gc(*prune_opts, auto=auto)
        else:
            paths = [ "--fork='%s'" % r.path for r in forks]
            status['fullcmd'] += ' ' + ' '.join(paths)

        if auto:
            status['fullcmd'] += ' --auto'
            if not need_to_gc(repository, expire=expire):
                return status
        else:
            _update_repack_all_options(expire=expire)

        git_process(git.pack_refs, all=True, prune=True)
        git_process(git.reflog, 'expire', all=True)
        git_process(git.repack, d=True, l=True, **_OPTS['repack_all'])

        que = BfsQue(repository, cnd_fn=lambda commit, repo: commit.id in repo)
        for f in forks:
            refs = f.listall_references()
            for ref in refs:
                ref_commit = f.lookup_reference(ref).get_object()
                que.search(ref_commit)
        commits = [str(c.id) for c in que.data]
        git_process(git.prune, *commits, expire=expire)
        git_process(git.rerere, 'gc')
    except Exception as e:
        print >>sys.stderr, e
        status['returncode'] = -1
    return status

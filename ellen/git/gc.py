# -*- coding: utf-8 -*-
import os
import re
import sys
from functools import wraps
from ellen.utils.process import git_with_repo

P_COMMIT = re.compile(r"^([0-9a-f]{40})\s+commit$")
P_OBJ = re.compile(r"^[0-9a-f]{38}$")

AGGRESSIVE_WINDOW = 250
AUTO_THRESHOLD = 6700
AUTO_PACK_LIMIT = 50
EXPIRE = '2.weeks.ago'
REPACK_ALL_OPTS = {'a': None, 'A': None, 'unpack_unreachable': None}


def check_status(f):
    @wraps(f)
    def wrapper(*a, **kw):
        status = f(*a, **kw)
        if status['returncode'] != 0:
            raise RuntimeError("'%s' failed during git.multi_gc" % f.__name__)
        return status
    return wrapper


@check_status
def git_log(git, *a, **kw):
    return git.log(*a, **kw)


@check_status
def git_pack_refs(git, *a, **kw):
    return git.pack_refs(*a, **kw)


@check_status
def git_reflog(git, *a, **kw):
    return git.reflog(*a, **kw)


@check_status
def git_repack(git, *a, **kw):
    return git.repack(*a, **kw)


@check_status
def git_prune(git, *a, **kw):
    return git.prune(*a, **kw)


@check_status
def git_rerere(git, *a, **kw):
    return git.rerere(*a, **kw)


def _update_repack_all_options(expire=EXPIRE):
    if "now" == expire:
        REPACK_ALL_OPTS['a'] = True
    elif expire:
        REPACK_ALL_OPTS['A'] = True
        REPACK_ALL_OPTS['unpack_unreachable'] = expire


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
        return  False
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


def gc_repository(repository, forks, auto=None, prune=None):
    """git gc command
    """
    expire = 'now' if prune == 'all' else prune
    if not expire:
        expire = EXPIRE

    try:
        git = git_with_repo(repository)
        status = {'returncode': 0, 'fullcmd': '%s multi-gc' % ' '.join(git.cmds), 'stderr': '', 'stdout': ''}
        if prune:
            prune_opt = "--prune=" + prune
            status['fullcmd'] += ' ' + prune_opt
        if not forks:
            return git.gc(prune_opt, auto=auto) if prune else git.gc(auto=auto)
        else:
            paths = [ "--fork='%s'" % r.path for r in forks]
            status['fullcmd'] += ' ' + ' '.join(paths)

        if auto:
            status['fullcmd'] += ' --auto'
            if not need_to_gc(repository, expire=expire):
                return status
        else:
            _update_repack_all_options(expire=expire)

        git_pack_refs(git, all=True, prune=True)
        git_reflog(git, 'expire', all=True)
        git_repack(git, d=True, l=True, a=REPACK_ALL_OPTS['a'],
                   A=REPACK_ALL_OPTS['A'],
                   unpack_unreachable=REPACK_ALL_OPTS['unpack_unreachable'])

        # seek commits to be pruned
        all_fork_commits = []
        commits = set()
        for f in forks:
            fork_git = git_with_repo(f)
            all_fork_commits += git_log(fork_git, '--pretty=format:%H', all=True)['stdout'].splitlines()
        for line in git_prune(git, dry_run=True, expire=expire)['stdout'].splitlines():
            matcher = P_COMMIT.search(line)
            if matcher:
                commits.add(matcher.group(1))
        commits &= set(all_fork_commits)

        git_prune(git, *commits, expire=expire)
        git_rerere(git, 'gc')
    except Exception as e:
        print >>sys.stderr, e
        status['returncode'] = -1
    return status

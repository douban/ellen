#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ellen.utils.process import git_with_repo
import os
import pygit2
import re
import sys

P_COMMIT = re.compile(r"^([0-9a-f]{40})\s+commit$")
P_OBJ = re.compile(r"^[0-9a-f]{38}$")

AGGRESSIVE_WINDOW = 250
AUTO_THRESHOLD = 6700
AUTO_PACK_LIMIT = 50
EXPIRE = '2.weeks.ago'

def gc_repository(repository, forks, aggressive=None, auto=None, quiet=None, 
                  prune=None):
    """git gc command
    """
    expire = 'now' if prune == 'all' else prune
    if not expire:
        expire = EXPIRE 
    repack_all_opts = {'a' : None, 'A' : None, 'unpack_unreachable' : None}

    def add_repack_all_options():
        if "now" == expire:
            repack_all_opts['a'] = True
        elif isinstance(prune, str):
            repack_all_opts['A'] = True
            repack_all_opts['unpack_unreachable'] = prune 
    
    def _too_many_loose_objects():
        obj_dir = os.path.join(repository.path, "objects/")
        if AUTO_THRESHOLD <= 0:
            return False
        auto_thr = (AUTO_THRESHOLD + 255) // 256
        if os.path.isdir(obj_dir):
            files = os.listdir(obj_dir)
            root = obj_dir
            if files:
                for f in files:
                    path = os.path.join(root, f)
                    if os.path.isdir(path):
                        root = path
                if root:
                    cnt = 0
                    for f in os.listdir(root):
                        path = os.path.join(root, f)
                        if os.path.isfile(path) and P_OBJ.search(f):
                            cnt = cnt + 1
                    if cnt > auto_thr:
                        return True
        return False
    
    def _too_many_packs():
        if AUTO_PACK_LIMIT <= 0:
            return False
        path = os.path.join(repository.path, "objects/info/packs")
        if os.path.isfile(path):
            with open(path, 'r') as f:
                lines = f.readlines()
                packs = len(lines) - 1
                if packs >= AUTO_PACK_LIMIT:
                    return True
        return False
    
    def need_to_gc():
        if AUTO_THRESHOLD <= 0:
            return False
        if _too_many_packs():
            add_repack_all_options()
        elif not _too_many_loose_objects():
            return False
        return True
    
    def filter_commits_for_prune(repo_commits):
        ret = []
        for f in forks:
            remote_branches = f.listall_branches(pygit2.GIT_BRANCH_REMOTE)
            for b in remote_branches:
                c = f.revparse_single(b).hex
                if not repo_commits or c in repo_commits:
                    ret.append(c)
        return list(set(ret))
    
    def check_status(status, action=None):
        print(status)
        if status['returncode'] != 0:
            raise RuntimeError("'%s' failed during git.multi_gc" % action)
    
    ret = {'returncode': 0, 'fullcmd': '', 'stderr': '', 'stdout': ''}
    try:
        # todo: function wrapper
        git = git_with_repo(repository)
        if not forks:
            return git.gc(aggressive=aggressive, auto=auto, quiet=quiet, 
                  prune=prune)
            
        if auto:
            if not need_to_gc():
                return ret
        else:
            add_repack_all_options()
        ret = git.pack_refs(all=True, prune=True)
        check_status(ret, action='pack-refs')

        ret = git.reflog('expire', all=True)
        check_status(ret, action='reflog')
        
        ret = git.repack(d=True, l=True, a=repack_all_opts['a'], 
                         A=repack_all_opts['A'], 
                         unpack_unreachable=repack_all_opts['unpack_unreachable'])
        check_status(ret, action='repack')
        
        # dry-run for commits in THIS repo to be pruned
        ret = git.prune(n=True, expire=expire)
        s = ret['stdout'].split('\n')
        commits = []
        for p in s:
            c = P_COMMIT.search(p)
            if c:
                commits.append(c.group(1))
        # seek commits will be prune truly and do pruning
        commits = filter_commits_for_prune(commits)
        ret = git.prune(commits, expire=expire)
        check_status(ret, action='prune')
        
        ret = git.rerere('gc')
        check_status(ret, action='rerere')
    except Exception as e:
        print >>sys.stderr, e 
    return ret

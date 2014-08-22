#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ellen.utils.process import git_with_repo
import os
import pygit2
import re
import sys

p_commit = re.compile(r"^([0-9a-f]{40})\s+commit$")
p_obj = re.compile(r"^[0-9a-f]{38}$")

aggressive_window = 250
gc_auto_threshold = 6700
gc_auto_pack_limit = 50
expire = '2.weeks.ago'

def gc_repository(repository, forks, aggressive=None, auto=None, quiet=None, 
                  prune=None):
    """git gc command
    """
    expire = prune if prune != 'all' else 'now'
    repack_all_opts = {'a' : None, 'A' : None, 'unpack_unreachable' : None}

    def add_repack_all_options():
        if "now" == expire:
            repack_all_opts['a'] = True
        elif isinstance(prune, str):
            repack_all_opts['A'] = True
            repack_all_opts['unpack_unreachable'] = prune 
    
    def _too_many_loose_objects():
        def get_a_dir(root, files):
            for f in files:
                path = os.path.join(root, f)
                if os.path.isdir(path):
                    return path
        
        obj_dir = os.path.join(repository.path, "objects/")
        if gc_auto_threshold <= 0:
            return False
        auto_thr = (gc_auto_threshold + 255) // 256
        if os.path.isdir(obj_dir):
            files = os.listdir(obj_dir)
            if files:
                root = get_a_dir(obj_dir, files)
                if root:
                    cnt = 0
                    for f in os.listdir(root):
                        path = os.path.join(root, f)
                        if os.path.isfile(path) and p_obj.search(f):
                            cnt = cnt + 1
                    if cnt > auto_thr:
                        return True
        return False
    
    def _too_many_packs():
        if gc_auto_pack_limit <= 0:
            return False
        path = os.path.join(repository.path, "objects/info/packs")
        if os.path.isfile(path):
            with open(path, 'r') as f:
                lines = f.readlines()
                packs = len(lines) - 1
                if packs >= gc_auto_pack_limit:
                    return True
        return False
    
    def need_to_gc():
        if gc_auto_threshold <= 0:
            return False
        if _too_many_packs():
            add_repack_all_options()
        elif not _too_many_loose_objects():
            return False
        return True
    
    def get_commit_in_lines(s):
        s = s.split('\n')
        ret = []
        for p in s:
            c = p_commit.search(p)
            if c:
                ret.append(c.group(1))
        return ret
                
    def add_fork_commits(repo_commits):
        commits = []
        for f in forks:
            remote_branches = f.listall_branches(pygit2.GIT_BRANCH_REMOTE)
            for b in remote_branches:
                c = f.revparse_single(b).hex
                if not repo_commits or c in repo_commits:
                    commits.append(c)
        return list(set(commits))
    
    def check_status(status, action=None):
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
        
        git = git_with_repo(repository)
        # todo: subcommand
        ret = git.reflog('expire', all=True)
        check_status(ret, action='reflog')
        
        git = git_with_repo(repository)
        ret = git.repack(d=True, l=True, a=repack_all_opts['a'], 
                         A=repack_all_opts['A'], 
                         unpack_unreachable=repack_all_opts['unpack_unreachable'])
        check_status(ret, action='repack')
        
        git = git_with_repo(repository)
        ret = git.prune(n=True, expire=expire)
        commits = get_commit_in_lines(ret['stdout']) 
        commits = add_fork_commits(commits)
        # todo: is it `--expire <expire>` ok?
        ret = git.prune(commits, expire=expire)
        check_status(ret, action='prune')
        
        git = git_with_repo(repository)
        ret = git.rerere('gc')
        check_status(ret, action='rerere')
    except Exception as e:
        print >>sys.stderr, e 
    return ret

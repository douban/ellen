#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ellen.utils.process import git_with_repo
import logging
import pygit2
import re
import sys

logger = logging.getLogger()

p_commit = re.compile(r"^([0-9a-f]{40})\s+commit$")

def gc_repository(repository, forks, aggressive=None, auto=None, quiet=None, 
                  prune=None):
    """git gc command
    """
    
    def repack_all_option():
        ret = {'a' : None, 'A' : None, 'unpack_unreachable' : None}
        if "now" == prune:
            ret['a'] = True
        elif isinstance(prune, str):
            ret['A'] = True
            ret['unpack_unreachable'] = prune 
        return ret
    
    def get_commit_in_lines(s):
        s = s.split('\n')
        ret = []
        for p in s:
            c = p_commit.search(p)
            if c:
                ret.append(c.group(1))
                
    def add_fork_commits(forks, items=None):
        commits = []
        for f in forks:
            remote_branches = f.listall_branches(pygit2.GIT_BRANCH_REMOTE)
            for b in remote_branches:
                c = f.revparse_single(b).hex
                if not items or c in items:
                    commits.append(c)
        return list(set(commits))
    
    def check_status(status, action):
        if status['returncode'] != 0:
            raise RuntimeError("'%s' failed during git.multi_gc" % action)
        print(ret)
    
    ret = None
    try:
        # todo: function wrapper
        git = git_with_repo(repository)
        if forks is None or len(forks) == 0:
            return git.gc(aggressive=aggressive, auto=auto, quiet=quiet, 
                  prune=prune)
            
        ret = git.pack_refs(all=True, prune=True)
        check_status(ret, 'pack-refs')
        
        git = git_with_repo(repository)
        # todo: subcommand
        ret = git.reflog('expire', all=True)
        check_status(ret, 'reflog')
        
        git = git_with_repo(repository)
        opts = repack_all_option()
        ret = git.repack(d=True, l=True, a=opts['a'], A=opts['A'], 
                   unpack_unreachable=opts['unpack_unreachable'])
        check_status(ret, 'repack')
        
        git = git_with_repo(repository)
        ret = git.prune(n=True, expire=prune)
        commits = get_commit_in_lines(ret['stdout']) 
        commits = add_fork_commits(forks, items=commits)
        # todo: is it `--expire <expire>` ok?
        ret = git.prune(commits, expire=prune)
        check_status(ret, 'prune')
        
        git = git_with_repo(repository)
        ret = git.rerere('gc')
        check_status(ret, 'rerere')
    except Exception as e:
        print >>sys.stderr, e 
    return ret

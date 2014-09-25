# -*- coding: utf-8 -*-


def list_branches(repository):
    branches = []
    refs = repository.listall_references()
    for ref in refs:
        if ref.startswith("refs/heads/"):
            branches.append(Branch(ref[11:]))
    return branches


class Branch(object):

    def __init__(self, name):
        self.name = name

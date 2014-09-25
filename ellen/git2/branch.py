# -*- coding: utf-8 -*-
from .reference import Reference


def list_branches(repository):
    branches = []
    refs = repository.listall_references()
    for ref in refs:
        if ref.startswith("refs/heads/"):
            branches.append(Branch(ref[11:]))
    return branches


class Branch(Reference):

    def __init__(self, name):
        self.name = name

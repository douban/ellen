# -*- coding: utf-8 -*-


def list_tags(repository):
    tags = []
    refs = repository.listall_references()
    for ref in refs:
        if ref.startswith("refs/tags/"):
            tags.append(Tag(ref[10:]))
    return tags


class Tag(object):

    def __init__(self, name):
        self.name = name

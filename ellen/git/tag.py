#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_COMMIT
from pygit2 import Signature

from ellen.utils.format import format_tag
from ellen.utils.format import format_lw_tag


def list_tags(repository, name_only=None):
    """git tag command, pygit2 wrapper"""
    tags = []
    refs = repository.listall_references()
    for ref in refs:
        if ref.startswith("refs/tags/"):
            if name_only:
                tags.append(ref.rpartition('/')[-1])
                continue
            # this is a tag but maybe a lightweight tag
            tag_obj = repository.revparse_single(ref)
            if tag_obj and tag_obj.type == GIT_OBJ_COMMIT:
                # lightweight tag
                tags.append(format_lw_tag(ref, tag_obj, repository))
            elif tag_obj and tag_obj.type == GIT_OBJ_TAG:
                tags.append(format_tag(tag_obj, repository))
    return tuple(tags)


def create_tag(repository, name, ref, author_name, author_email, message):
    obj = repository.revparse_single(ref)
    if obj.type == GIT_OBJ_COMMIT:
        signature = Signature(author_name, author_email)
        oid = repository.create_tag(name, str(obj.id), GIT_OBJ_COMMIT,
                                    signature, message)
        return oid and str(oid)
    else:
        return None

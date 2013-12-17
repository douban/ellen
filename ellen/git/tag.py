#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_COMMIT

from ellen.utils.format import format_tag
from ellen.utils.format import format_lw_tag


def list_tags(repository, name_only=None):
    """git tag command, pygit2 wrapper"""
    tags = []
    refs = repository.listall_references()
    for ref in refs:
        if ref.startswith("refs/tags/"):
            if name_only:
                tags.append(ref[10:])
                continue
            # this is a tag but maybe a lightweight tag
            tag_obj = repository.revparse_single(ref)
            if tag_obj and tag_obj.type == GIT_OBJ_COMMIT:
                # lightweight tag
                tags.append(format_lw_tag(ref, tag_obj, repository))
            elif tag_obj and tag_obj.type == GIT_OBJ_TAG:
                tags.append(format_tag(tag_obj, repository))
    return tuple(tags)

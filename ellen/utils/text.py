#!/usr/bin/env python
# -*- coding: utf-8 -*-


def trunc_utf8(string, num, etc="..."):
    """truncate a utf-8 string, show as num chars.
    arg: string, a utf-8 encoding string; num, look like num chars
    return: a utf-8 string
    """
    try:
        gb = string.decode("utf8", "ignore")
    except UnicodeEncodeError:  # Already decoded
        gb = string
    gb = gb.encode("gb18030", "ignore")
    if num >= len(gb):
        return string
    if etc:
        etc_len = len(etc.decode("utf8", "ignore").encode("gb18030", "ignore"))
        trunc_idx = num - etc_len
    else:
        trunc_idx = num
    ret = gb[:trunc_idx].decode("gb18030", "ignore").encode("utf8")
    if etc:
        ret += etc
    return ret

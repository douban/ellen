#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dealing with internal diff
"""

import difflib


def _get_context(lines):
    top = []
    middle = []
    bottom = []
    top_line_num = 0
    bottom_line_num = 0
    for (attr, line) in lines:
        if attr != ' ':
            break
        top_line_num += 1
        line = line.rstrip('\n')
        top.append([' ', ' ' + line])
    for (attr, line) in lines[::-1]:
        if attr != ' ':
            break
        bottom_line_num += 1
        line = line.rstrip('\n')
        bottom.append([' ', ' ' + line])
    if bottom_line_num == 0:
        middle = lines[top_line_num:]
    else:
        middle = lines[top_line_num:-bottom_line_num]
        bottom.reverse()

    too_big = False
    if len(middle) > 32:
        too_big = True
    else:
        for (attr, line) in middle:
            if len(line) >= 512:
                too_big = True
                break

    return top, middle, bottom, too_big


def _get_old(lines):
    ''' filter old lines '''
    _lines = []
    for (attr, line) in lines:
        # FIXME: newline
        if attr not in ('+', '<', '>', '='):
            if attr in ('>', '='):
                # split first '\n'
                line = line[1:]
            # ^M, 0x0D 0x0A
            line = line.rstrip('\n')
            _lines.append(line)
    return _lines
    #return [line for (attr, line) in lines if attr not in ('+', '>')]


def _get_new(lines):
    ''' filter new lines '''
    _lines = []
    for (attr, line) in lines:
        # FIXME: newline
        if attr not in ('-', '>', '<', '='):
            if attr in ('<', '='):
                # split first '\n'
                line = line[1:]
            line = line.rstrip('\n')
            _lines.append(line)
    return _lines
    #return [line for (attr, line) in lines if attr not in ('-', '<', '>')]


def _strip_old_line(line):
    if line.startswith('\x00-') and line.endswith('\x01'):
        stripped_line = line[2:-1]
        if '\x01' in stripped_line:
            return line
        return stripped_line
    return line


def _strip_new_line(line):
    if line.startswith('\x00+') and line.endswith('\x01'):
        stripped_line = line[2:-1]
        if '\x01' in stripped_line:
            return line
        return stripped_line
    return line


def _traditional(generator):
    new_lines = []
    # TODO: strip more sensible.
    for old, new, changed in generator:
        if changed:
            if not old[0]:
                line = _strip_new_line(new[1])
                #yield ('+', '+' + line)
                new_lines.append(('+', '+' + line))
            elif not new[0]:
                line = _strip_old_line(old[1])
                yield ('-', '-' + line)
            else:
                line = _strip_old_line(old[1])
                yield ('-', '-' + line)
                line = _strip_new_line(new[1])
                #yield ('+', '+' + line)
                new_lines.append(('+', '+' + line))
        else:
            for line in new_lines:
                yield line
            new_lines = []
            yield (' ', ' ' + old[1])
    # last lines
    for line in new_lines:
        yield line
    new_lines = []


def _ntraditinal(generator):
    for line in generator:
        yield (line[0], line[1:])


def _side_by_side(generator, side=None):
    for old, new, changed in generator:
        if changed:
            if not old[0]:
                line = _strip_new_line(new[1])
                if side:
                    if side == 'old':
                        yield ('', ' ')
                    else:
                        yield ('+', '+' + line)
                else:
                    yield ((' ', ' '), ('+', line))
            elif not new[0]:
                line = _strip_old_line(old[1])
                if side:
                    if side == 'old':
                        yield ('-', '-' + line)
                    else:
                        yield ('', ' ')
                else:
                    yield (('-', line), (' ', ' '))
            else:
                lline = _strip_old_line(old[1])
                rline = _strip_new_line(new[1])
                if side:
                    if side == 'old':
                        yield ('-', '-' + lline)
                    else:
                        yield ('+', '+' + rline)
                else:
                    yield (('-', lline), ('+', rline))
        else:
            if side:
                if side == 'old':
                    yield (' ', ' ' + old[1])
                else:
                    yield (' ', ' ' + old[1])
            else:
                yield ((' ', ' ' + old[1]), (' ', ' ' + old[1]))


def _raw(lines, side=None):
    # TODO: fix '>', '>', '='
    _lines = []
    for (attr, line) in lines:
        # ^M, 0x0D 0x0A
        line = line.rstrip('\n')
        if attr == '+':
            if side:
                if side == 'old':
                    _lines.append([' ', ' '])
                else:
                    _lines.append([attr, attr + line])
            else:
                _lines.append([attr, attr + line])
        elif attr == '-':
            if side:
                if side == 'old':
                    _lines.append([attr, attr + line])
                else:
                    _lines.append([' ', ' '])
            else:
                _lines.append([attr, attr + line])
        elif attr == ' ':
            _lines.append([attr, attr + line])
        elif attr == '<':
            line = line[1:]
            if side:
                if side == 'old':
                    _lines.append([' ', ' '])
                else:
                    _lines.append(['+', '+' + line])
            else:
                _lines.append(['+', '+' + line])
        elif attr == '>':
            line = line[1:]
            if side:
                if side == 'old':
                    _lines.append(['-', '-' + line])
                else:
                    _lines.append([' ', ' '])
            else:
                _lines.append(['-', '-' + line])
        elif attr == '=':
            line = line[1:]
            _lines.append([' ', ' ' + line])
    return _lines


def _get_mdiff(lines):
    ''' return difflib._mdiff generator '''
    old = _get_old(lines)
    new = _get_new(lines)
    return difflib._mdiff(old, new)


def mdiff2(lines):
    top, middle, bottom, too_big = _get_context(lines)
    if not too_big:
        _mdiff = _get_mdiff(middle)
        return list(_mdiff)
    else:
        return None


# TODO: ...
def hunk2(lines, mdiff, side_by_side=None):
    top, middle, bottom, too_big = _get_context(lines)
    if too_big:
        _hunk = _raw(middle, side=side_by_side)
    else:
        if side_by_side:
            _hunk = _side_by_side(mdiff, side=side_by_side)
        else:
            _hunk = _traditional(mdiff)
    for line in top:
        yield line
    for line in _hunk:
        yield list(line)
    for line in bottom:
        yield line

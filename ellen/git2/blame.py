# -*- coding: utf-8 -*-

from pygit2 import (GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES,
                    GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES)


def blame(repository):
    blob = repository.revparse_single("%s:%s" % (ref, path))
    if not blob or is_blob_binary(blob):
        return None
    lines = blob.data.splitlines()
    if lineno:
        if lineno <= 0 and lineno > len(lines):
            return None

    flags = (GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES
             | GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES)
    commit = repository.revparse_single(ref)
    if not commit:
        return None
    newest_commit = commit.id
    blame = repository.blame(path, flags, newest_commit=newest_commit, **kw)
    if not blame:
        return None

    hunks = []
    if lineno:
        hunk = blame.for_line(lineno)
        hunks.append(format_blame_hunk(hunk,
                                       repository))
    else:
        # FIXME: if line in blame hunk, It should not be blamed again.
        for hunk in blame:
            hunks.append(format_blame_hunk(hunk,
                                           repository))
    return blob, hunks

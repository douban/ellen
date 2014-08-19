# -*- coding: utf-8 -*-

import urlparse
from StringIO import StringIO

try:
    from ConfigParser import RawConfigParser
except ImportError:
    # NOTICE: this module changed name to `configparser` in python 3.x
    from configparser import RawConfigParser


def list_submodules(repository, reference):
    return


def get_submodule(repository, reference, path):
    try:
        rev = "%s:.gitmodules" % reference
        blob = repository.revparse_single(rev)
        modules = _parse_submodule(repository, blob)
    except (ValueError, KeyError):
        # TODO: raise ellen error
        return

    submodule = {}
    submodule['host'] = None
    submodule['url'] = None

    section_name = ('submodule "{submodule_name}"'.format(submodule_name=path))
    if modules and modules.has_section(section_name):
        submodule.update(dict(modules.items(section_name)))

    url = submodule.get('url')
    if url:
        submodule['host'] = _parse_submodule_url(submodule['url'])
        if url.endswith('.git'):
            submodule['url'] = url[:-4]

    return submodule


def _parse_submodule(repository, submodule_obj):
    submodule_conf_raw = submodule_obj.data
    submodule_conf_raw = _format_submodule_conf(submodule_conf_raw)

    config = RawConfigParser(allow_no_value=True)
    config.readfp(StringIO(submodule_conf_raw))

    return config


def _format_submodule_conf(raw):
    if isinstance(raw, unicode):
        lines = raw.splitlines()
    elif isinstance(raw, str):
        lines = raw.decode("UTF-8").splitlines()
    else:
        return None

    lines = map(lambda line: line.strip(), lines)
    return "\n".join(lines)


def _parse_submodule_url(url):
    parser = urlparse.urlparse(url)
    netloc = parser.netloc

    if not netloc:
        # for scp-like url, e.g. git@github.com:xxxx/xxx.git
        if parser.path == url:
            netloc = parser.path.split(':')[0].split('@')[-1]
        else:
            return url
    return netloc

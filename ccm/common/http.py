# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    import urllib2
except ImportError:
    from urllib import request as urllib2


def post(url=None, body=None, headers={}, timeout=120):
    req = urllib2.Request(url, body, headers)
    try:
        rep = urllib2.urlopen(req, timeout=timeout)
        return rep.code, rep.read()
    except urllib2.HTTPError as rep:
        if rep:
            return rep.code, rep.read()
        else:
            raise

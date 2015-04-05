#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GNU General Public Licence (GPL)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
# Copyright (c) 2015 by OXullo Intersecans / bRAiNRAPERS


from __future__ import unicode_literals

import ConfigParser
import StringIO
import logging
import requests
import pykka

logger = logging.getLogger(__name__)

def pls_parse(data):
    fp_data = StringIO.StringIO(data)
    playlist = ConfigParser.ConfigParser()
    playlist.readfp(fp_data)

    urls = []
    for i in xrange(1, playlist.getint('playlist', 'numberofentries') + 1):
        urls.append(playlist.get('playlist', 'File%d' % i))

    return urls

class PlaylistFetcher(pykka.ThreadingActor):
    def fetch(self, url):
        try:
            request = requests.get(url)
            urls = pls_parse(request.text)
        except Exception, e:
            logger.error(e)
            return []
        else:
            return urls


if __name__ == '__main__':
    import log

    log.init()
    fetcher = PlaylistFetcher.start().proxy()
    print fetcher.fetch('http://somafm.com/groovesalad.pls').get()
    fetcher.stop()

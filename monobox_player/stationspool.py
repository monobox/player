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

import logging
import requests
import pykka

logger = logging.getLogger(__name__)

class StationsPool(pykka.ThreadingActor):
    def __init__(self, stations_url):
        super(StationsPool, self).__init__()
        self._stations = []
        self._stations_pool = []
        self._stations_url = stations_url

    def on_start(self):
        self.refresh()

    def next_station(self):
        if not self._stations:
            logger.info('Stations pool is empty, starting over')
            self._stations = self._stations_pool[:]

        return self._stations.pop()

    def refresh(self):
        logging.info('Refreshing stations pool')
        request = requests.get(self._stations_url)
        self._stations_pool = request.json()['urls']
        self._stations = self._stations_pool[:]
        logging.info('%d stations loaded' % len(self._stations_pool))


if __name__ == '__main__':
    import log

    log.init(debug=True)

    client = StationsPool.start('http://api.monobox.net/random').proxy()
    for i in xrange(300):
        print client.next_station().get()

    client.stop()

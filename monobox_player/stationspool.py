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
    def __init__(self, base_url, auth_code):
        super(StationsPool, self).__init__()
        self._stations = []
        self._base_url = base_url
        if self._base_url[-1] == '/':
            self._base_url = self._base_url[:-1]
        self._auth_code = auth_code
        self._session_id = None

        self.register()

    def next_station(self):
        if not self._stations:
            logger.info('Stations pool is empty, getting new list')
            self.load_stations()

        return self._stations.pop()

    def register(self):
        request = requests.post(self._compose('register'), data={'auth_code': self._auth_code})
        # TODO: proper failure handling
        payload = request.json()
        self._session_id = payload['session_id']

    def load_stations(self):
        logging.info('Refreshing stations pool')
        # TODO: GET or POST?
        request = requests.get(self._compose('stations'), params={'session_id': self._session_id})
        self._stations = request.json()['urls']
        logging.info('%d stations loaded' % len(self._stations))

    def _compose(self, resource):
        return '%s/%s' % (self._base_url, resource)

if __name__ == '__main__':
    import log

    log.init(debug=True)

    client = StationsPool.start('http://localhost:8887', '1234567890').proxy()
    for i in xrange(10):
        print client.next_station().get()

    client.stop()

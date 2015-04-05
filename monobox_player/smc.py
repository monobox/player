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

import threading
import re
import serial
import logging
import pykka

import listener


logger = logging.getLogger(__name__)


class SMCListener(listener.Listener):
    @staticmethod
    def send(event, **kwargs):
        listener.send_async(SMCListener, event, **kwargs)

    def volume_changed(self, new_volume):
        pass

    def powered_on(self):
        pass

    def powered_off(self):
        pass

    def button_pressed(self):
        pass


class SMC(pykka.ThreadingActor):
    def __init__(self, port):
        super(SMC, self).__init__()
        try:
            self._serial = serial.Serial(port, 115200, timeout=.5)
        except Exception as error:
            raise RuntimeError('SMC serial connection failed: %s' % error)

        self._buffer = ''
        self._is_on = False

    def on_start(self):
        self._serial.flushInput()
        thread = threading.Thread(target=self._thread_run)
        thread.start()

    def on_stop(self):
        self._running = False

    def is_on(self):
        return self._is_on

    def _thread_run(self):
        self._running = True
        while self._running:
            ch = self._serial.read()
            if ch not in ('', '\r'):
                self._buffer += ch

            # logger.debug('SMC buf: %s' % str([c for c in self.buffer]))

            while '\n' in self._buffer:
                self._process_line(self._buffer[0:self._buffer.find('\n')])
                self._buffer = self._buffer[self._buffer.find('\n') + 1:]

    def _process_parsed(self, typ, value):
        if typ == 'P':
            self._is_on = bool(value)
            if value:
                SMCListener.send('powered_on')
            else:
                SMCListener.send('powered_off')
        elif typ == 'V':
            SMCListener.send('volume_changed', new_volume=value)
        elif typ == 'B' and value == 1:
            if value:
                SMCListener.send('button_pressed')

    def _process_line(self, line):
        logger.debug('SMC process line: %s' % line)
        res = re.search(r'^([BPV]):(\-?\d+)$', line)
        if res:
            typ, value = res.groups()
            try:
                value = int(value)
            except ValueError:
                logger.warning('Cannot decode value %s (line=%s)' % (value, line))
            else:
                self._process_parsed(typ, value)


if __name__ == '__main__':
    from gi.repository import GObject
    import log

    class TestListener(pykka.ThreadingActor, SMCListener):
        def volume_changed(self, new_volume):
            logging.info('Volume: %d' % new_volume)

        def powered_on(self):
            logging.info('Powered ON')

        def powered_off(self):
            logging.info('Powered OFF')

        def button_pressed(self):
            logging.info('Button pressed')

    log.init(debug=True)
    test_listener = TestListener.start()
    smc = SMC.start('/dev/ttyACM0')

    main_loop = GObject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass

    smc.stop()
    test_listener.stop()
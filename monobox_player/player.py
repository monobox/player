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
import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

GObject.threads_init()
Gst.init(None)

logger = logging.getLogger(__name__)

class Player(object):
    def __init__(self):
        self.playbin = Gst.ElementFactory.make('playbin', 'playbin')
        fakesink = Gst.ElementFactory.make('fakesink', 'fakesink')
        self.playbin.set_property('video-sink', fakesink)
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

    def play(self, url):
        self.playbin.set_state(Gst.State.NULL)
        self.playbin.set_property('uri', url)
        self.playbin.set_state(Gst.State.PLAYING)

    def on_message(self, bus, message):
        logger.info('on_message: %s' % str(message))

        t = message.type
        if t == Gst.MessageType.EOS:
            self.playbin.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            self.playbin.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            logger.error('Error: %s (debug=%s)' % (err, debug))


if __name__ == '__main__':
    import log

    log.init()
    player = Player()
    player.play('http://uwstream1.somafm.com:80')

    main_loop = GObject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass
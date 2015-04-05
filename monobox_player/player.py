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
import pykka

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

import listener

GObject.threads_init()
Gst.init(None)

logger = logging.getLogger(__name__)

GST_PLAY_FLAG_VIDEO = (1 << 0)
GST_PLAY_FLAG_AUDIO = (1 << 1)
GST_PLAY_FLAG_TEXT = (1 << 2)
GST_PLAY_FLAG_VIS = (1 << 3)
GST_PLAY_FLAG_SOFT_VOLUME = (1 << 4)
GST_PLAY_FLAG_NATIVE_AUDIO = (1 << 5)
GST_PLAY_FLAG_NATIVE_VIDEO = (1 << 6)
GST_PLAY_FLAG_DOWNLOAD = (1 << 7),
GST_PLAY_FLAG_BUFFERING = (1 << 8)


class PlayerListener(listener.Listener):
    @staticmethod
    def send(event, **kwargs):
        listener.send_async(PlayerListener, event, **kwargs)

    def playback_error(self, code, message):
        pass


class Player(pykka.ThreadingActor):
    def __init__(self):
        super(Player, self).__init__()

        self._playbin = Gst.ElementFactory.make('playbin', 'playbin')
        self._playbin.set_property('flags', GST_PLAY_FLAG_AUDIO)
        bus = self._playbin.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_gst_message)

    def play(self, url):
        self.stop_playback()
        self._playbin.set_property('uri', url)
        self._playbin.set_state(Gst.State.PLAYING)

    def stop_playback(self):
        self._playbin.set_state(Gst.State.NULL)

    def set_volume(self, level):
        self._playbin.set_property('volume', level)
        logger.debug('Volume level set to %.2f' % level)

    def _on_gst_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR:
            self._playbin.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            logger.error('Error: %s (debug=%s)' % (err, debug))
            PlayerListener.send('playback_error', code=err.code, message=err.message)


if __name__ == '__main__':
    import log

    class TestListener(pykka.ThreadingActor, PlayerListener):
        def playback_error(self, code, message):
            logger.info('Got error code=%s message=%s' % (code, message))

    log.init(debug=True)
    test_listener = TestListener.start()

    player = Player.start()
    player_proxy = player.proxy()

    player_proxy.play('http://uwstream1.somafm.com:80/').get()

    main_loop = GObject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass

    test_listener.stop()
    player.stop()
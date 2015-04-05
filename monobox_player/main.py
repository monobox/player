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

import pykka

import player
import smc
import playlist
import stationspool
import log

class Main(pykka.ThreadingActor, player.PlayerListener, smc.SMCListener):
    def on_start(self):
        self._stationspool = stationspool.StationsPool.start('http://api.monobox.net/random').proxy()
        self._playlist = playlist.PlaylistFetcher.start().proxy()
        self._player = player.StreamPlayer.start().proxy()
        self._feedback = player.FeedbackPlayer('assets', 0.5)
        self._smc = smc.SMC.start('/dev/ttyACM0').proxy()

    def on_stop(self):
        self._smc.stop()
        self._feedback.stop()
        self._player.stop()
        self._playlist.stop()
        self._stationspool.stop()

    def powered_off(self):
        self._player.stop_playback()
        self._stationspool.refresh().get()

    def powered_on(self):
        self.play_next()

    def volume_changed(self, new_volume):
        self._player.set_volume(new_volume).get()

    def button_pressed(self):
        if self._smc.is_on().get():
            self._feedback.play('click')
            self.play_next()

    def playback_error(self, code, message):
        self.play_next()

    def play_next(self):
        while True:
            urls = self._playlist.fetch(self._stationspool.next_station().get()).get()
            if urls:
                break

        self._player.play(urls[0]).get()

def run():
    from gi.repository import GObject

    log.init(debug=True)
    main = Main.start()

    main_loop = GObject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass

    main.stop()


if __name__ == '__main__':
    run()

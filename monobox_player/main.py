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
import pykka
from gi.repository import GObject

import player
import smc
import playlist
import stationspool
import log
import config

logger = logging.getLogger(__name__)


class Main(pykka.ThreadingActor, player.PlayerListener, smc.SMCListener):
    def on_start(self):
        self._stationspool = stationspool.StationsPool.start(config.get('stations_pool', 'api_url')).proxy()
        self._playlist = playlist.PlaylistFetcher.start().proxy()
        self._player = player.StreamPlayer.start().proxy()
        self._feedback = player.FeedbackPlayer(config.get('feedback_player', 'assets_path'),
                                               config.getfloat('feedback_player', 'volume'))
        # TODO: wrap smc initialisation to prevent lockups
        self._smc = smc.SMC.start(config.get('smc', 'serial_port')).proxy()

    def on_stop(self):
        self._smc.stop()
        self._feedback.stop()
        self._player.stop()
        self._playlist.stop()
        self._stationspool.stop()

    def powered_off(self):
        self._player.stop_playback()
        # TODO: the refresh happens twice at startup, since the smc reports powered_off
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
            playlist_url = self._stationspool.next_station().get()
            urls = self._playlist.fetch(playlist_url).get()
            if urls:
                break
            else:
                logger.warning('Empty playlist at url %s' % playlist_url)

        self._player.play(urls[0]).get()


def run():
    # TODO: CAE with log vs config initialization (debug mode, output file)
    log.init()
    config.init()

    main = Main.start()

    main_loop = GObject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass

    main.stop()


if __name__ == '__main__':
    run()

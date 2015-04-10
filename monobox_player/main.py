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

import sys
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


class MainController(pykka.ThreadingActor, player.PlayerListener, smc.SMCListener):
    def __init__(self, plumbing):
        super(MainController, self).__init__()
        self.plumbing = plumbing

    def powered_off(self):
        self.plumbing.player.stop_playback()
        # TODO: the refresh happens twice at startup, since the smc reports powered_off
        self.plumbing.stations_pool.refresh().get()

    def powered_on(self):
        self.play_next()

    def volume_changed(self, new_volume):
        self.plumbing.player.set_volume(new_volume).get()

    def button_pressed(self):
        if self.plumbing.smc.is_on().get():
            self.plumbing.feedback.play('click')
            self.play_next()

    def playback_error(self, code, message):
        self.play_next()

    def play_next(self):
        while True:
            playlist_url = self.plumbing.stations_pool.next_station().get()
            urls = self.plumbing.playlist.fetch(playlist_url).get()
            if urls:
                break
            else:
                logger.warning('Empty playlist at url %s' % playlist_url)

        self.plumbing.player.play(urls[0]).get()


class Plumbing(object):
    def setup(self):
        try:
            self.smc = smc.SMC.start(config.get('smc', 'serial_port')).proxy()
        except Exception, e:
            logger.error('Cannot initialize SMC: %s' % str(e))
            raise

        self.stations_pool = stationspool.StationsPool.start(config.get('stations_pool', 'api_url')).proxy()
        self.playlist = playlist.PlaylistFetcher.start().proxy()
        self.player = player.StreamPlayer.start().proxy()
        self.feedback = player.FeedbackPlayer(config.get('feedback_player', 'assets_path'),
                                               config.getfloat('feedback_player', 'volume'))
        self._main_controller = MainController.start(self)

    def teardown(self):
        self.smc.stop()
        self.feedback.stop()
        self.player.stop()
        self.playlist.stop()
        self.stations_pool.stop()
        self._main_controller.stop()


def run():
    # TODO: CAE with log vs config initialization (debug mode, output file)
    log.init()
    config.init()

    plumbing = Plumbing()
    try:
        plumbing.setup()
    except Exception, e:
        logger.exception(e)
        sys.exit(1)

    main_loop = GObject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass

    plumbing.teardown()


if __name__ == '__main__':
    run()

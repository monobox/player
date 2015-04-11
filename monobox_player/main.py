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
        self.plumbing.feedback.play('powerdown')

    def powered_on(self):
        self.plumbing.feedback.play('powerup')
        self.plumbing.stations_pool.load_stations().get()
        self.play_next()

    def volume_changed(self, new_volume):
        self.plumbing.player.set_volume(new_volume).get()

    def button_pressed(self):
        if self.plumbing.smc.is_on().get():
            self.plumbing.feedback.play('next')
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


class Component(object):
    def __init__(self, tag, klass, **kargs):
        self.tag = tag
        self.klass = klass
        self.kargs = kargs
        self.proxy = None

    def start(self):
        self.proxy = self.klass.start(**self.kargs).proxy()

    def stop(self):
        if self.proxy:
            self.proxy.stop()


class Plumbing(object):
    def setup(self):
        self.components = [Component('smc', smc.SMC, port=config.get('smc', 'serial_port')),
                      Component('playlist', playlist.PlaylistFetcher),
                      Component('stations_pool', stationspool.StationsPool,
                                base_url=config.get('stations_pool', 'base_url'),
                                auth_code=config.get('stations_pool', 'auth_code')),
                      Component('player', player.StreamPlayer),
                      Component('feedback', player.FeedbackPlayer,
                                assets_base_path=config.get('feedback_player', 'assets_base_path'),
                                volume=config.getfloat('feedback_player', 'volume')),
                      Component('main_controller', MainController, plumbing=self)]

        try:
            for component in self.components:
                component.start()
                self.__dict__[component.tag] = component.proxy
        except Exception, e:
            self.teardown()
            raise

    def teardown(self):
        for component in self.components:
            component.stop()



def run():
    # TODO: CAE with log vs config initialization (debug mode, output file)
    log.init(True)
    config.init()

    plumbing = Plumbing()
    try:
        plumbing.setup()
    except Exception, e:
        logger.exception(e)
        plumbing.teardown()
        sys.exit(1)

    main_loop = GObject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass

    plumbing.teardown()


if __name__ == '__main__':
    run()

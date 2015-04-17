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
import time
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
        try:
            self.plumbing.stations_pool.load_stations().get()
        except Exception, e:
            logger.exception(e)
            self.plumbing.feedback.play('error')
        else:
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
            try:
                playlist_url = self.plumbing.stations_pool.next_station().get()
                urls = self.plumbing.playlist.fetch(playlist_url).get()
            except Exception, e:
                logger.exception(e)
                self.plumbing.feedback.play('error')
                return

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
        self.feedback = None
        self.components = [
                Component('feedback', player.FeedbackPlayer,
                        assets_base_path=config.get('feedback_player', 'assets_base_path'),
                        volume=config.getfloat('feedback_player', 'volume')),
                Component('smc', smc.SMC, port=config.get('smc', 'serial_port')),
                Component('playlist', playlist.PlaylistFetcher),
                Component('stations_pool', stationspool.StationsPool,
                        base_url=config.get('stations_pool', 'base_url'),
                        auth_code=get_auth_code()),
                Component('player', player.StreamPlayer),
                Component('main_controller', MainController, plumbing=self)
        ]

        for component in self.components:
            component.start()
            self.__dict__[component.tag] = component.proxy

    def run(self):
        try:
            self.setup()
            self.feedback.play('intro').get()
            main_loop = GObject.MainLoop()
            main_loop.run()
        except KeyboardInterrupt:
            self.teardown()
            return 0
        except Exception, e:
            logger.exception(e)
            self._play_error()

            holdoff = config.getfloat('main', 'error_holdoff_time')
            if holdoff > 0:
                logger.info('Waiting %.2fs before exiting' % holdoff)
                time.sleep(holdoff)

            self.teardown()
            return 1

    def teardown(self):
        for component in self.components:
            component.stop()

    def _play_error(self):
        if self.feedback is not None:
            main_loop = GObject.MainLoop()

            self.feedback.play('error').get()
            self.feedback.set_on_eos_callback(main_loop.quit)
            main_loop.run()

def run():
    # TODO: CAE with log vs config initialization (debug mode, output file)
    log.init()

    plumbing = Plumbing()
    sys.exit(plumbing.run())

def get_auth_code():
    auth_code = config.get('main', 'auth_code')
    if not auth_code:
        # http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
        import fcntl, socket, struct

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', str('eth0')))
        auth_code = ':'.join(['%02x' % ord(char) for char in info[18:24]])

    logging.info('Auth code: %s' % auth_code)

    return auth_code

if __name__ == '__main__':
    run()

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

# Copied from mopidy

from __future__ import absolute_import, unicode_literals

import logging

from gi.repository import GObject

import pykka

logger = logging.getLogger(__name__)


def send_async(cls, event, **kwargs):
    GObject.idle_add(lambda: send(cls, event, **kwargs))


def send(cls, event, **kwargs):
    listeners = pykka.ActorRegistry.get_by_class(cls)
    logger.debug('Sending %s to %s: %s', event, cls.__name__, kwargs)
    for listener in listeners:
        # Save time by calling methods on Pykka actor without creating a
        # throwaway actor proxy.
        #
        # Because we use `.tell()` there is no return channel for any errors,
        # so Pykka logs them immediately. The alternative would be to use
        # `.ask()` and `.get()` the returned futures to block for the listeners
        # to react and return their exceptions to us. Since emitting events in
        # practise is making calls upwards in the stack, blocking here would
        # quickly deadlock.
        listener.tell({
            'command': 'pykka_call',
            'attr_path': ('on_event',),
            'args': (event,),
            'kwargs': kwargs,
        })

class Listener(object):

    def on_event(self, event, **kwargs):
        """
        Called on all events.

        *MAY* be implemented by actor. By default, this method forwards the
        event to the specific event methods.

        :param event: the event name
        :type event: string
        :param kwargs: any other arguments to the specific event handlers
        """
        getattr(self, event)(**kwargs)

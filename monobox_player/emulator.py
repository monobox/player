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

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import smc

class EmulatorWindow(Gtk.Window):
    def __init__(self):
        super(EmulatorWindow, self).__init__(title='Monobox player')

        self._is_on = False
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)

        slider = Gtk.HScale()
        slider.set_digits(0)
        slider.set_range(0, 100)
        slider.connect('value-changed', self._on_volume_changed)
        box.pack_start(slider, True, True, 0)

        button = Gtk.Button('Button')
        button.connect('clicked', self._on_button)
        box.add(button)

        self.resize(300, 100)

    def _on_volume_changed(self, slider):
        value = slider.get_value()
        if value > 0 and not self._is_on:
            smc.SMCListener.send('powered_on')
            self._is_on = True

        if value == 0 and self._is_on:
            smc.SMCListener.send('powered_off')
            self._is_on = False

        smc.SMCListener.send('volume_changed', new_volume=float(value/100.0))

    def _on_button(self, button):
        smc.SMCListener.send('button_pressed')


if __name__ == '__main__':
    window = EmulatorWindow()
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()

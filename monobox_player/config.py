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
import argparse
import logging
import ConfigParser
import StringIO

DEFAULT_CONFIG='''[main]
error_holdoff_time=5
auth_code=
emulator=false

[stations_pool]
base_url=http://api.monobox.net/

[feedback_player]
assets_base_path=assets
volume=0.05

[smc]
serial_port=/dev/ttyACM0
'''

logger = logging.getLogger(__name__)


class ConfigManager(object):
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(StringIO.StringIO(DEFAULT_CONFIG))

        self._remaining_args = None
        self._base_parser = argparse.ArgumentParser(
                formatter_class=argparse.RawDescriptionHelpFormatter,
                add_help=False)
        self._base_parser.add_argument('--debug', action='store_true', help='print debug log messages')
        self._base_parser.add_argument('--config', help='specify a configuration file')
        self._base_parser.add_argument('--dump-config', action='store_true', help='dump default configuration file')

    def load_config(self, path):
        self.config.read(path)

    def early_parse(self, argv):
        args, self._remaining_args = self._base_parser.parse_known_args(argv)

        if args.dump_config:
            self.config.write(sys.stdout)
            sys.exit(0)

        return args

    def augment_config(self):
        parser = argparse.ArgumentParser(parents=[self._base_parser],
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        for section in self.config.sections():
            group = parser.add_argument_group('%s section' % section)
            for option in self.config.options(section):
                option_tag = '%s.%s' % (self._demangle(section), self._demangle(option))
                current_value = self.config.get(section, option)

                group.add_argument('--%s' % option_tag, default=current_value, help='Config override')

        args = parser.parse_args(self._remaining_args)

        for key, value in args.__dict__.iteritems():
            if value is not None and '.' in key:
                section, option = key.split('.', 1)
                self.config.set(section, option, value)

    def _demangle(self, text):
        return text.replace('_', '-').lower()


manager = ConfigManager()

# Patch ConfigParser query methods to the module level
me = sys.modules[__name__]
for meth in ['get', 'getint', 'getfloat', 'getboolean']:
    setattr(me, meth, getattr(manager.config, meth))


if __name__ == '__main__':
    import sys

    c = ConfigManager()
    print 'Early parse: %s' % str(c.early_parse(sys.argv[1:]))
    print 'New config: %s' % str(c.augment_config())
    c.config.write(sys.stdout)

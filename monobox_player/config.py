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
import os
import logging
import argparse
import ConfigParser


logger = logging.getLogger(__name__)
_inst = None

def init(config_file=None):
    global _inst

    if config_file is None:
        parser = argparse.ArgumentParser(description='monobox player')
        parser.add_argument('config', help='configuration file')

        args = parser.parse_args()
        config_file = args.config

    if not os.path.isfile(config_file):
        logging.error('Cannot file config file %s' % config_file)
        sys.exit(1)
    else:
        logging.info('Loading config from %s' % config_file)
    _inst = ConfigParser.ConfigParser()
    _inst.read(config_file)

    me = sys.modules[__name__]
    for meth in ['get', 'getint', 'getfloat', 'getboolean']:
        setattr(me, meth, getattr(_inst, meth))

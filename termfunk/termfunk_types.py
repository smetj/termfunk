#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termfunk_types.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import os
import sys
import getpass


class Choice(object):
    def __init__(self, items=[]):

        if not isinstance(items, list):

            raise Exception("Choices should be a list")

        else:
            self.choices = items

    def __str__(self):

        return "<Choice: %s>" % (", ".join(self.choices))

    def __iter__(self):

        for item in self.choices:
            yield item


class EnvOrAsk(object):
    def __init__(self, name=None, secret=False):

        self.name = name
        self.env_name = "%s_%s" % (sys.argv[0].split("/")[-1].upper(), name.upper())
        self.secret = secret

    def __str__(self):
        if self.env_name in os.environ:
            if self.secret:
                return "<$%s **********>" % (self.env_name)
            else:
                return "<$%s %s>" % (self.env_name, os.environ[self.env_name])
        else:
            return "<$%s> or <Interactive>" % (self.env_name)

    def get(self):

        if self.env_name in os.environ:
            return os.environ[self.env_name]
        else:
            try:
                return getpass.getpass("Value for %s: " % (self.name))
            except KeyboardInterrupt:
                print()
                print("ctrl+c by user.")
                sys.exit(0)


class Ask(object):
    def __init__(self, secret=False):
        self.secret = secret

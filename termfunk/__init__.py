#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

import argparse
import inspect
import sys
import getpass
import os


class ArgumentDefaultsHelpFormatter(argparse.HelpFormatter):
    """Help message formatter which adds default values to argument help.

    Only the name of this class is considered a public API. All the methods
    provided by the class are considered an implementation detail.
    """

    def _get_help_string(self, action):
        help = action.help
        if "%(default)" not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += "%(default)s"
        return help


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


class TermFunk(object):
    def __init__(self, description="TermFunk", width="80"):

        os.environ["COLUMNS"] = str(width)

        # Parse arguments
        parser = argparse.ArgumentParser(description=description)

        # Add the "function" subparser
        subparsers = parser.add_subparsers(dest="function")
        subparsers.required = True

        # Add the "list" function as a function
        subparsers.add_parser("list", description="Lists all available functions.")

        # Add the user defined functions a subparsers
        self.__addUserFunctionsAsSubparsers(subparsers)

        # Parse CLI provided arguments
        args = parser.parse_args()
        args = vars(args)

        # Extract the function from the arguments
        function = args["function"]
        del (args["function"])

        # Complete any variables for which we need to ask user input
        args = self.__askUserValues(args)

        # Execute the desired function
        try:
            self.__executeUserFunction(function, args)
        except Exception as err:
            print(err)
            sys.exit(1)
        else:
            sys.exit(0)

    def __addUserFunctionsAsSubparsers(self, subparsers):
        """
        Completes a argparse subparser instance with a subparser per user
        defined function including the function's arguments.

        Args:
            subparser (_SubParsersAction): The subparser instance.
        """

        for function in self.__list():
            s = subparsers.add_parser(
                function[9:],
                description="".join(getattr(self, function).__doc__.split("\n")[:2]),
                formatter_class=ArgumentDefaultsHelpFormatter,
            )
            for key, value in inspect.signature(
                getattr(self, function)
            ).parameters.items():
                if value.default == inspect._empty:
                    # positional arg
                    s.add_argument(key)
                else:
                    # keyword
                    if isinstance(value.default, Ask):
                        default_value = EnvOrAsk(key, value.default.secret)
                    else:
                        default_value = value.default
                    s.add_argument("--%s" % (key), default=default_value, help=": ")

        return subparsers

    def __askUserValues(self, args):

        for var, value in args.items():
            if isinstance(value, EnvOrAsk):
                args[var] = value.get()
        return args

    def __executeUserFunction(self, name, args):

        if "function_%s" % name in self.__list():
            getattr(self, "function_%s" % name)(**args)
        else:
            getattr(self, name)()

    def __list(self):
        """
        Finds and lists all available user defined functions.

        Args:
            None

        Returns:
            list: A list of fuction names.
        """

        functions = []
        for item in dir(self):
            if callable(getattr(self, item)) and item.startswith("function_"):
                functions.append(item)
        return functions

    def list(self):

        for item in dir(self):
            if callable(getattr(self, item)) and item.startswith("function_"):
                print(item[9:])

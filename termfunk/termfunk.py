#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termfunk.py
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

from .termfunk_types import Choice
from .termfunk_types import Ask
from .termfunk_types import EnvOrAsk
from .helpformatter import ArgumentDefaultsHelpFormatter
from .bash_complete import BASH_COMPLETE

import argparse
import inspect
import sys
import os
import jinja2


class TermFunk(object):
    def __init__(self, description="TermFunk", width="80"):

        os.environ["COLUMNS"] = str(width)

        # Parse arguments
        parser = argparse.ArgumentParser(description=description)

        # Add the "function" subparser
        subparsers = parser.add_subparsers(dest="function")
        subparsers.required = True

        # Add the "complete" function as a function
        subparsers.add_parser("complete", description="Lists all available functions.")

        # Add the user defined functions a subparsers
        self.__addUserFunctionsAsSubparsers(subparsers)

        # Parse CLI provided arguments
        args = parser.parse_args()
        args = vars(args)

        # Extract the function from the arguments
        function = args["function"]
        del (args["function"])

        # Complete any variables for which we need to ask user input
        self.args = self.__askUserValues(args)

        # Execute the desired function
        try:
            self.__executeUserFunction(function, self.args)
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
            docstring = getattr(self, function).__doc__
            if docstring is None:
                description = ""
            else:
                description = "".join(
                    [line for line in docstring.split("\n") if line != ""]
                )
            s = subparsers.add_parser(
                function[9:],
                description=description,
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
            getattr(self, name)(**args)

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

    def complete(self):

        complete_map = self.__getCompleteMap()
        env = jinja2.Environment()
        env.filters["ischoice"] = self.__isChoice
        print(
            env.from_string(BASH_COMPLETE).render(
                script_name=self.__getScriptName(), function_map=complete_map
            )
        )

    def __getCompleteMap(self):

        complete_map = {}
        for function in self.__list():
            complete_map[function[9:]] = {}
            for var_name, var_value in inspect.signature(
                getattr(self, function)
            ).parameters.items():
                complete_map[function[9:]].update(
                    {"--%s" % (var_name): var_value.default}
                )
                # if var_value.default != inspect._empty and isinstance(
                #     var_value.default, list
                # ):
                #     complete_map[function[9:]].update(
                #         {"--%s" % (var_name): var_value.default}
                #     )
                # else:
                #     complete_map[function[9:]].update({"--%s" % (var_name): {}})
        return complete_map

    def __getScriptName(self):

        return sys.argv[0].split("/")[-1].lower()

    def __isChoice(self, value):
        return isinstance(value, Choice)

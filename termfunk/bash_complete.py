#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bash_complete.py
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


BASH_COMPLETE = """
_termfunk_{{ script_name }}_complete()
{
  local cur prev

  COMPREPLY=()
  cur=${COMP_WORDS[COMP_CWORD]}
  prev=${COMP_WORDS[COMP_CWORD-1]}
  command=${COMP_WORDS[1]}

  # Handling the first command
  if [ $COMP_CWORD -eq 1 ]; then
    COMPREPLY=( $(compgen -W '{{ " ".join(function_map.keys()) }}' -- $cur) )
    return 0

  {%- for function, vars in function_map.items() %}
      {%- for var in vars %}
        {%- if function_map[function][var]|ischoice %}
  elif [ $command == "{{ function }}" ] && [ $prev == "{{ var }}" ]; then
      COMPREPLY=( $(compgen -W '{{ " ".join(function_map[function][var]) }}' -- $cur) )
        {%- endif %}
      {%- endfor %}
  elif [ $command == "{{ function }}" ]; then
    COMPREPLY=( $(compgen -W '{{ " ".join(vars.keys()) }}' -- $cur) )
    return 0
  {%- endfor %}
  fi
} &&
complete -F _termfunk_{{ script_name }}_complete {{ script_name }}
"""

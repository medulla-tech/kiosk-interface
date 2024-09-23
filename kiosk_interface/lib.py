#!/usr/bin/python3
# coding: utf-8
"""This module launch the kiosk interface"""
#
# (c) 2022 Siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

class Singleton(object):
    _instances = {}
    def instance(func):
        def wrapper(*args, **kwargs):
            if func not in Singleton._instances:
                Singleton._instances[func] = func(*args, **kwargs)
            return Singleton._instances[func]
        return wrapper

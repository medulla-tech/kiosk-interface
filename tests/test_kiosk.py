#!/usr/bin/python3
# coding: utf-8
"""Test the kiosk module"""
#
# (c) 2018-2022 Siveo, http://www.siveo.net
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

from PyQt6.QtWidgets import QApplication
import sys

try:
    from kiosk_interface.kiosk import Kiosk
except BaseException:
    from kiosk import Kiosk


class TestKiosk:
    app = QApplication(sys.argv)
    kiosk = Kiosk(app)

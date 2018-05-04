#!/usr/bin/env python3
# coding: utf-8
"""Declare the Tray object"""
#
# (c) 2018 Siveo, http://www.siveo.net
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

import sys

from PyQt5.QtWidgets import QWidget
from kiosk import Kiosk

from views.tray import tray_main_view


class Tray(QWidget):
    """This class define the system tray object. This is the first controller called by the app."""

    def __init__(self):
        """Initialization of the TrayIcon"""
        super().__init__()
        self.criterion = ""
        self.main_window = None

        # Call the view for the System Tray
        tray_main_view(self)

        # Bind the actions
        self.open_action.triggered.connect(self.open)
        if hasattr(self, 'input_search'):
            self.input_search.textChanged.connect(self.criterion_modified)

    def open(self):
        """This method is called if the event 'open' is launched"""
        self.main_window = Kiosk(self.criterion)
        self.main_window.show()

    def quit(self):
        """This method is called if the event 'quit' is launched"""
        sys.exit()

    def criterion_modified(self):
        """This method is called when the search criterion is modified """
        self.criterion = self.input_search.text()

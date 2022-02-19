#!/usr/bin/python3
# coding: utf-8
"""Declare the Tray object"""
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

import sys


from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QWidgetAction
try:
    from kiosk_interface.views.custom_search_bar import CustomSearchBar
except:
    from views.custom_search_bar import CustomSearchBar
from PyQt5.QtGui import QCursor
import threading

class Tray(QSystemTrayIcon):
    """This class define the system tray object. This is the first controller called by the app."""

    def __init__(self, app):
        """Initialization of the TrayIcon"""
        super().__init__()
        self.app = app
        self.app.tray = self

        self.criterion = ""

        # Call the view for the System Tray
        msg = self.app.translate("Tray", 'Launch the tray')
        self.app.logger("info","%s" % msg)

        self.icon = QIcon("datas/kiosk.png")

        self.setToolTip(self.app.translate("Tray", "Kiosk"))
        self.setIcon(self.icon)

        # With this the kiosk is always running even if the main window is closed.
        self.setVisible(True)

        self.menu = QMenu()
        # The searchbar is not added if the kiosk is running on Mac OS
        if sys.platform != "darwin":
            self.search_action = QWidgetAction(self.menu)
            self.input_search = CustomSearchBar(self.app, self)
            self.search_action.setDefaultWidget(self.input_search)

        # Add the open option to the menu
        if hasattr(self, 'search_action'):
            self.menu.addAction(self.search_action)
        self.open_action = QAction(self.app.translate("Tray", "Open"))
        self.open_action.setParent(self.menu)
        self.menu.addAction(self.open_action)

        # Add the menu to the tray
        self.setContextMenu(self.menu)

        # Bind the actions
        if sys.platform != "darwin":
            self.activated.connect(self.open_menu)  # left click action for Windows and Linux
        self.open_action.triggered.connect(self.open)

        # Connect the input_search from the menu with actions, only for Windows and Linux OS
        if hasattr(self, 'input_search'):
            self.input_search.changed.connect(self.update_criterion)
            self.input_search.clicked.connect(self.open)

    def open(self):
        """This method is called if the event 'open' is launched. Use it as midddleware"""
        initialize = threading.Thread(target=self.app.send, args=('{"action":"kioskinterface",\
                                                                  "subaction":"initialization"}',))
        initialize.start()
        if hasattr(self, 'input_search'):
            self.app.notifier.tray_action_open.emit(self.input_search.text)
        else:
            self.app.notifier.tray_action_open.emit("")

    def open_menu(self):
        """Method used to open the menu from the tray with left click. Use it as middleware"""
        cursor = QCursor()
        self.menu.popup(cursor.pos())

    def update_criterion(self):
        self.criterion = self.input_search.text

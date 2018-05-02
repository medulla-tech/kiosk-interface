#!/usr/bin/env python3
# coding: utf-8
#
# (c) 2018 siveo, http://www.siveo.net
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
from PyQt5.QtWidgets import QWidget, QSystemTrayIcon, QMenu, QAction, QWidgetAction, QLineEdit
from KioskMainWindow import KioskMainWindow


class TrayIcon(QWidget):
    def __init__(self):
        super().__init__()

        # Create the icon
        self.icon = QIcon("kiosk.png")
        # Create the tray
        self.tray = QSystemTrayIcon(self)
        # Set the icon of the tray
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)

        # Create the tray menu
        self.menu = QMenu(self)

        # Create the tray actions
        self.search_action = QWidgetAction(self.menu)
        self.search_action.setDefaultWidget(QLineEdit(text="Search package"))
        self.open_action = QAction("Open")
        self.quit_action = QAction("Quit")

        # Add the tray actions to the tray menu
        self.menu.addAction(self.search_action)
        self.menu.addAction(self.open_action)
        self.menu.addAction(self.quit_action)

        # Create the main windows for the kiosk
        self.main_view = KioskMainWindow()
        # Associate action with event
        self.bind_menu_action(self.open_action, self.main_view.show)
        self.bind_menu_action(self.quit_action, sys.exit)

        # Add the menu to the tray
        self.tray.setContextMenu(self.menu)

    def bind_menu_action(self, action, function):
        action.triggered.connect(function)

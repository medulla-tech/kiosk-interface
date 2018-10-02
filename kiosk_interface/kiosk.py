#!/usr/bin/env python3
# coding: utf-8
"""Declare the Kiosk object"""
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

from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QListWidget, QLineEdit, QLabel, QTabWidget, \
    QGridLayout
from kiosk_interface.views.custom_package_item import CustomPackageWidget
from kiosk_interface.views.tab_kiosk import TabKiosk
from kiosk_interface.views.tab_notification import TabNotification

import re


class Kiosk(QWidget):
    """This class define the main window of the kiosk"""

    def __init__(self, app):
        """
            Initialize the kiosk object. 
            This object set up the mechanism to control the kiosk window
            Params:
                app: QApplication is a reference of the main application
        """
        super().__init__()
        self.app = app

        self.resize(self.app.parameters.width, self.app.parameters.height)

        self.app.logger("info", self.app.translate("Application", "Kiosk main view initialization"))
        self.tab_kiosk = TabKiosk(self.app, self)
        self.tab_notification = TabNotification(self.app, self)

        self.tabs = QTabWidget(self.app.kiosk)
        self.tabs.addTab(self.tab_kiosk, "Packages")
        self.tabs.addTab(self.tab_notification, "Notifications")
        self.tab_notification.add_notification("Kiosk main view initialization")

        grid = QGridLayout(self.app.kiosk)
        grid.addWidget(self.tabs, 1,1,1,1)


        self.setLayout(grid)
    def show(self):
        super().show()
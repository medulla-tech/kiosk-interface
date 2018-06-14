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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import pyqtSignal

from models import Package, get_datakiosk
from views.custom_package_item import CustomPackageWidget
from views.kiosk import kiosk_main_view

import re


class Kiosk(QWidget):
    """This class define the main window of the kiosk"""
    updated = pyqtSignal(name="updated")

    def __init__(self, criterion, app):
        """
            Initialize the kiosk object. 
            This object set up the mechanism to controll the kiosk window
        """
        super().__init__()
        self.parent_app = app

        # If the search bar in the tray is not shown the criterion is set to False.
        # So with this test the problem doesn't occurs.
        if criterion is False:
            self.criterion = ""
        else:
            self.criterion = criterion

        # Get the packages list and genere the display objects
        self.packages_list = None
        self.items_list = None
        self.searchbar = None
        self.list = None

        self.init_ui()

    def filter_packages(self, criterion):
        if criterion:
            self.criterion = criterion
        else:
            if self.searchbar.text() != self.criterion:
                self.criterion = self.searchbar.text()

        if self.criterion == "":
            self.result_list = self.packages_list

        self.list.clear()
        self.result_list = []

        for item in self.packages_list:
            if re.search(self.criterion, item.getname(), flags=re.IGNORECASE):
                self.result_list.append(item)

        self.items_list = []
        # For each package found, an item is created
        for package in self.result_list:
            self.items_list.append({'item': QListWidgetItem(self.list),
                                   'item_package': CustomPackageWidget(package, "list")})

        # Attach each item to the list
        for element in self.items_list:
            element['item'].setSizeHint(element['item_package'].sizeHint())

            self.list.addItem(element['item'])
            self.list.setItemWidget(element['item'], element['item_package'])

            # Update the general layout
            self.tabs_content[1].setLayout(self.tabs_content[1].layout)

    def select_row(self):
        """select_row get the actual row and listen if there are any action launched. If an action is launched,
        the appropriate message is generated and send to agent-machine."""
        selected_item = self.list.itemWidget(self.list.currentItem())

        # Kind of messages the kiosk needs to return to the agent
        # {'uuid' : "45d4-3124c21-3123", "action": "kioskinterfaceinstall", "subaction" : "install"}

    def init_ui(self):
        self.packages_list = self.result_list = Package.get_all(self)

        kiosk_main_view(self)

        # Link the tray search criterion with the main search bar
        self.searchbar.setText(self.criterion)
        self.filter_packages(self.criterion)
        self.searchbar.textChanged.connect(self.filter_packages)

        self.list.itemSelectionChanged.connect(self.select_row)
        self.updated.connect(self.datas_update)

    def datas_update(self):
        """This method get the list of all packages and generate the main window"""
        self.packages_list = self.result_list = Package.get_all(self)
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)
        self.setLayout(self.layout())
        self.init_ui()

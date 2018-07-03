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

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import pyqtSignal
from models import Package, get_datakiosk
from views.custom_package_item import CustomPackageWidget
from views.kiosk import kiosk_main_view
from server import MessengerToAM
import threading
import re


class Kiosk(QWidget):
    """This class define the main window of the kiosk"""
    updated = pyqtSignal(name="updated")

    def __init__(self, criterion, app, caller):
        """
            Initialize the kiosk object. 
            This object set up the mechanism to controll the kiosk window
        """
        super().__init__()
        self.parent_app = app
        self.caller = caller
        self.send('{"action":"kioskLog","type":"info","message":"Kiosk main view initialization"}')
        self.first_open = True

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

        self.packages_list = self.result_list = Package.get_all(self)
        self.send('{"action":"kioskLog","type":"info","message":"Show kiosk main window"}')
        self.init_ui()

    def filter_packages(self, criterion):
        self.send('{"action":"kioskLog","type":"info","message":"Search criterion changed : %s"}' % criterion)
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
        package_names = []
        for package in self.result_list:
            package_names.append(package.getname())
            tmp = QListWidgetItem(self.list)
            tmp1 = CustomPackageWidget(package, "list")
            tmp.setSizeHint(tmp1.sizeHint())

            self.list.addItem(tmp)
            self.list.setItemWidget(tmp, tmp1)
            self.tabs_content[1].setLayout(self.tabs_content[1].layout)
        self.send('{"action":"kioskLog","type":"info","message":"Package found : %s"}'%' '.join(package_names))

    def select_row(self):
        """select_row get the actual row and listen if there are any action launched. If an action is launched,
        the appropriate message is generated and send to agent-machine."""
        selected_item = self.list.itemWidget(self.list.currentItem())
        self.updated.emit()
        # Kind of messages the kiosk needs to return to the agent
        # {'uuid' : "45d4-3124c21-3123", "action": "kioskinterfaceinstall", "subaction" : "install"}

    def init_ui(self):
        self.first_open = False
        kiosk_main_view(self)

        # Link the tray search criterion with the main search bar
        self.searchbar.setText(self.criterion)
        self.filter_packages(self.criterion)
        self.searchbar.textChanged.connect(self.filter_packages)

        self.list.itemSelectionChanged.connect(self.select_row)
        self.updated.connect(self.datas_update)

    def datas_update(self):
        """This method get the list of all packages and generate the main window"""
        self.send('{"action":"kioskLog","type":"info","message":"Reload kiosk main window"}')

        self.list.clear()

        packages = get_datakiosk()

        for package in packages:
            package_object = Package(package)
            tmp = QListWidgetItem(self.list)
            tmp1 = CustomPackageWidget(package_object, "list")
            tmp.setSizeHint(tmp1.sizeHint())
            self.list.addItem(tmp)
            self.list.setItemWidget(tmp, tmp1)
            self.tabs_content[1].setLayout(self.tabs_content[1].layout)

    def send(self, message, parallel=True):
        """Send the specified message to the agent machine
                Params:
                    message: string which represent the commande launched into the agent machine.
                    parallel: boolean representing a flag if the message will be send un a thread or not
                """

        client = MessengerToAM()
        if parallel:
            thread = threading.Thread(target=client.send, args=(message.encode('utf-8'),))
            thread.start()
        else:
            client.send(message.encode('utf-8'))

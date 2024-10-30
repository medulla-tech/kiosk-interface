#!/usr/bin/python3
# coding: utf-8
"""Declare the kiosk space for the app"""
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

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from kiosk_interface.views.custom_package_item import CustomPackageWidget
except BaseException:
    from views.custom_package_item import CustomPackageWidget

import re


class TabKiosk(QWidget):
    """This class define the main window of the kiosk"""

    def __init__(self, app, kiosk):
        """
        Initialize the kiosk object.
        This object set up the mechanism to control the kiosk window
        Params:
            app: QApplication is a reference of the main application
        """
        super().__init__()
        self.app = app
        self.app.kiosk = kiosk
        self.app.logger("info", "Kiosk main view initialization")

        self.app.notifier.server_status_changed.connect(self.status_changed)
        self.resize(self.app.parameters.width, self.app.parameters.height)

        self.label_status = QLabel(self.app.translate("Kiosk", "Status : Disconnected"))
        self.status_changed()
        self.label_last_inventory = QLabel(
            f"Last Inventory : {self.app.last_inventory or 'N/A'}"
        )

        # Create a horizontal layout to display both the status and the inventory
        self.status_inventory_layout = QHBoxLayout()
        self.status_inventory_layout.addWidget(self.label_status)

        # Add a spacer to push the last inventory to the right
        self.status_inventory_layout.addItem(
            QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )

        self.status_inventory_layout.addWidget(self.label_last_inventory)

        self.input_search = QLineEdit(self.app.tray.criterion, self)
        self.input_search.setPlaceholderText("Search a package by name")

        self.button_refresh = QPushButton("Refresh", self)
        self.button_refresh.clicked.connect(self.on_refresh_clicked)

        self.item_custom_packages = []
        self.custom_packages = []
        self.list_wrapper = QListWidget()
        self.list_wrapper.resize(self.width(), self.height())
        self.lay = QVBoxLayout()
        self.lay.addLayout(
            self.status_inventory_layout
        )
        self.lay.addWidget(self.input_search)
        self.lay.addWidget(self.button_refresh)
        self.lay.addWidget(self.list_wrapper)
        self.setLayout(self.lay)

        # TODO : Show list as grid
        # TODO : give the possibility to choose between grid and list (preference saved in config file)
        # https://stackoverflow.com/questions/37331270/how-to-create-grid-style-qlistwidget

        self.input_search.textChanged.connect(self.search)
        self.update_last_inventory_display()

    def show(self):
        """Displays the main window for the kiosk package manager"""

        # Firstly the search action is launched because it refresh the UI with the latest packages.
        # Moreover if a criterion is given, the search method update the
        # package list with corresponding packages
        self.search()
        super().show()

    def search(self):
        """Refresh the list of custom package and the custom packages itself if the search criterion is found in the
        name of the package."""
        self.list_wrapper.clear()
        self.item_custom_packages = []
        self.custom_packages = []
        flag = False
        for package in self.app.packages:
            if "name" not in package or "uuid" not in package:
                continue
            if "action" not in package:
                package["action"] = []
            if self.input_search.text() != "":
                if re.search(
                    self.input_search.text(), package["name"], flags=re.IGNORECASE
                ):
                    item_widget = QListWidgetItem(self.list_wrapper)
                    custom_package = CustomPackageWidget(self.app, package)
                    item_widget.setSizeHint(custom_package.sizeHint())
                    self.custom_packages.append(custom_package)
                    self.item_custom_packages.append(item_widget)

                    self.list_wrapper.addItem(item_widget)
                    self.list_wrapper.setItemWidget(item_widget, custom_package)

                if not flag:
                    flag = True
            else:
                item_widget = QListWidgetItem(self.list_wrapper)
                custom_package = CustomPackageWidget(self.app, package)
                item_widget.setSizeHint(custom_package.sizeHint())
                self.custom_packages.append(custom_package)
                self.item_custom_packages.append(item_widget)

                self.list_wrapper.addItem(item_widget)
                self.list_wrapper.setItemWidget(item_widget, custom_package)

    def status_changed(self):
        """Modify the status in the kiosk view"""
        msg = ""

        # For unknown reason self.app.translate return empty message.
        # It has for consequences an empty status
        if self.app.connected is False:
            msg = "Status : Disconnected"
        else:
            msg = "Status : Connected"
        self.label_status.setText(msg)

    def update_last_inventory_display(self):
        """Updates the display of the last inventory date."""
        if self.app.last_inventory:
            self.label_last_inventory.setText(
                f"Last Inventory : {self.app.last_inventory}"
            )
        else:
            self.label_last_inventory.setText("Last Inventory : N/A")

        self.button_refresh.setEnabled(True)
        self.button_refresh.setText("Refresh")

    def on_refresh_clicked(self):
        """Method called when the 'update' button is clicked"""
        self.button_refresh.setEnabled(False)
        self.button_refresh.setText("Refresh in progress...")

        self.app.send('{"action":"kioskinterface", "subaction":"initialization"}')
        self.app.send('{"action":"kioskinterface", "subaction":"inventory"}')

    def request_inventory(self):
        """Request the date of the last inventory to AM"""
        self.app.send('{"action":"kioskinterface", "subaction":"inventory"}')


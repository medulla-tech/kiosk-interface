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

from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QListWidget, QLineEdit, QLabel, QTabWidget
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

        if self.app.connected is False:
            self.label_status = QLabel(
                self.app.translate(
                    "Kiosk", "Status : Disconnected"))
        else:
            self.label_status = QLabel(
                self.app.translate(
                    "Kiosk", "Status : Connected"))
        self.input_search = QLineEdit(self.app.tray.criterion, self)
        self.input_search.setPlaceholderText("Search a package by name")

        self.item_custom_packages = []
        self.custom_packages = []
        self.list_wrapper = QListWidget()
        self.list_wrapper.resize(self.width(), self.height())
        self.lay = QVBoxLayout()
        self.lay.addWidget(self.label_status)
        self.lay.addWidget(self.input_search)
        self.lay.addWidget(self.list_wrapper)
        self.setLayout(self.lay)

        # TODO : Show list as grid
        # TODO : give the possibility to choose between grid and list (preference saved in config file)
        # https://stackoverflow.com/questions/37331270/how-to-create-grid-style-qlistwidget

        self.input_search.textChanged.connect(self.search)

    def show(self):
        """ Displays the main window for the kiosk package manager"""

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
            if self.input_search.text() != "":
                if re.search(
                        self.input_search.text(),
                        package["name"],
                        flags=re.IGNORECASE):
                    item_widget = QListWidgetItem(self.list_wrapper)
                    custom_package = CustomPackageWidget(self.app, package)
                    item_widget.setSizeHint(custom_package.sizeHint())
                    self.custom_packages.append(custom_package)
                    self.item_custom_packages.append(item_widget)

                    self.list_wrapper.addItem(item_widget)
                    self.list_wrapper.setItemWidget(
                        item_widget, custom_package)

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
        self.label_status.setText(msg)

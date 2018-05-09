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

from models import Package
from views.custom_package_item import CustomPackageWidget
from views.kiosk import kiosk_main_view
import re


class Kiosk(QWidget):
    """This class define the main window of the kiosk"""

    def __init__(self, criterion):
        """Initialize """
        super().__init__()
        self.criterion = criterion

        self.packages_list = self.result_list = Package.get_all(self)

        kiosk_main_view(self)
        self.searchbar.textChanged.connect(self.filter_packages)

    def filter_packages(self):
        if self.searchbar.text() != self.criterion:
            self.criterion = self.searchbar.text()

        if self.searchbar.text() == "":
            self.result_list = self.packages_list
        else:
            self.result_list = []
            for package in self.packages_list:
                if re.search(self.criterion, package.name, flags=re.IGNORECASE) and self.criterion != "":
                    self.result_list.append(package)

        for element in self.items_list:
            # Delete all the element in the list
            self.list.removeItemWidget(element['item'])

        # Regenerate the list
        for package in self.result_list:
            self.items_list.append({'item': QListWidgetItem(self.list),
                                   'item_package': CustomPackageWidget(package)})

        # Attach each item to the list
        for element in self.items_list:
            element['item'].setSizeHint(element['item_package'].sizeHint())

            self.list.addItem(element['item'])
            self.list.setItemWidget(element['item'], element['item_package'])
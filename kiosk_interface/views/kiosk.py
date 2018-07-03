#!/usr/bin/env python3
# coding: utf-8
""" Define the views for the Kiosk object"""
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

from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QLineEdit, QGridLayout, \
    QListWidget, QHBoxLayout, QScrollArea
from PyQt5.QtWidgets import QListWidgetItem
from views.custom_package_item import CustomPackageWidget
from PyQt5.QtCore import QCoreApplication


def kiosk_main_view(ref):
    """
    Define the main view for the kiosk window.
    param:
        ref is a reference to the Kiosk object
    """
    ref.setWindowTitle("Kiosk")
    ref.setLayout(QVBoxLayout(ref))
    # Tabs for differents kind of view

    ref.tabs = QTabWidget()

    ref.tabs_content = [QWidget(), QWidget()]
    ref.tabs.addTab(ref.tabs_content[1], "List")

    ref.searchbar = QLineEdit(ref)

    ref.items_grid = []

    # Tab "grid"
    ref.tabs_content[0].layout = QHBoxLayout(ref.tabs_content[0])
    ref.tabs_content[0].scroll = QScrollArea(ref.tabs_content[0])
    ref.tabs_content[0].scroll.setWidgetResizable(True)
    ref.tabs_content[0].scroll_content = QWidget()
    ref.tabs_content[0].grid = QGridLayout(ref.tabs_content[0].scroll_content)
    ref.tabs_content[0].scroll.setWidget(ref.tabs_content[0].scroll_content)
    ref.tabs_content[0].layout.addWidget(ref.tabs_content[0].scroll)

    # Tab "list"
    ref.tabs_content[1].layout = QVBoxLayout(ref.tabs)
    ref.list = QListWidget(ref.tabs_content[1])
    ref.tabs_content[1].layout.addWidget(ref.list)

    ref.list.adjustSize()
    ref.items_list = []
    # For each package found, an item is created

    for package in ref.result_list:
        ref.items_list.append({'item': QListWidgetItem(ref.list),
                               'item_package': CustomPackageWidget(package, "list")})

    # Attach each item to the list
    for element in ref.items_list:
        element['item'].setSizeHint(element['item_package'].sizeHint())

        ref.list.addItem(element['item'])
        ref.list.setItemWidget(element['item'], element['item_package'])

    # Update the general layout
    ref.tabs_content[1].setLayout(ref.tabs_content[1].layout)

    ref.searchbar.setPlaceholderText(QCoreApplication.translate("TrayIcon", "Search Package"))
    ref.layout().addWidget(ref.searchbar)
    ref.layout().addWidget(ref.tabs)

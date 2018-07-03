#!/usr/bin/env python3
# coding: utf-8
""" Define a partial view for the package in list mode"""
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

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout


class CustomSearchBar(QWidget):
    """This object is the specialized menu action which contains the searchbar."""
    def __init__(self):
        """Initialize the object"""
        super().__init__()

        self.layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(
            QCoreApplication.translate("TrayIcon", "Search Package"))
        self.btn_launch_search = QPushButton("search")

        self.layout.addWidget(self.input)
        self.layout.addWidget(self.btn_launch_search)
        self.setLayout(self.layout)

        self.textChanged = self.input.textChanged
        self.clicked = self.btn_launch_search.clicked
        self.text = self.input.text
        self.show()
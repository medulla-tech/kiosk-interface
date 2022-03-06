#!/usr/bin/python3
# coding: utf-8
""" Define a partial view for search bar in the tray"""
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

from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout


class CustomSearchBar(QWidget):
    """This object is the specialized menu action which contains the searchbar."""

    def __init__(self, app, ref):
        """Initialize the object"""
        super().__init__()
        self.app = app
        # It is an exception for all the app. Normally the tray is callable from self.app, but
        #
        self.tray = ref
        self.setParent(ref.menu)
        self.layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(self.app.translate("Tray", "Search Package"))
        self.btn_launch_search = QPushButton(self.app.translate("Tray", "search"))

        self.layout.addWidget(self.input)
        self.layout.addWidget(self.btn_launch_search)
        self.setLayout(self.layout)

        self.clicked = self.btn_launch_search.clicked
        self.changed = self.input.textChanged
        self.text = self.input.text()

        self.input.textChanged.connect(self.update_text)

    def update_text(self):
        self.text = self.input.text()

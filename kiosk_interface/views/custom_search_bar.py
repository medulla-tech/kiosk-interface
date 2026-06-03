#!/usr/bin/python3
# coding: utf-8
""" Define a partial view for search bar in the tray"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout


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

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

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QLineEdit, QGridLayout, QPushButton, \
    QListWidget, QLabel, QHBoxLayout

class CustomPackageWidget(QWidget):
    def __init__(self, package):
        super().__init__()

        self.icon = QLabel("")
        icon = QPixmap("datas/" + package.icon)
        icon = icon.scaled(24, 24)
        self.icon.setPixmap(icon)
        self.name = QLabel(package.name)

        mini_layout = QHBoxLayout()
        mini_layout.addWidget(self.icon)
        mini_layout.addWidget(self.name)

        self.description = QLabel(package.description)
        self.version = QLabel(package.version)

        self.actions = []
        for action in package.actions:
            self.actions.append(QPushButton(action))

        self.layout = QGridLayout(self)

        # self.layout.addWidget(self.icon, 0, 0)
        # self.layout.addWidget(self.name, 0, 1)
        self.layout.addLayout(mini_layout, 0, 0)
        self.layout.addWidget(self.version, 0, 1)
        self.layout.addWidget(self.description, 0, 2)

        column = 0
        while column < len(self.actions):
            self.layout.addWidget(self.actions[column], 1, column)
            column += 1

        self.setLayout(self.layout)

        self.show()

    def getname(self):
        return self.name.text()

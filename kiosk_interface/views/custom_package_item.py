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
from models import send_message_to_am
import os

class CustomPackageWidget(QWidget):
    def __init__(self, package, type="grid"):
        super().__init__()
        self.type = type
        self.icon = QLabel("")
        self._message = ""
        icon = QPixmap("datas/" + package.icon)
        if self.type == "list":
            icon = icon.scaled(24, 24)
        else:
            icon = icon.scaled(50, 50)

        self.icon.setPixmap(icon)
        self.name = QLabel(package.name)
        self.description = QLabel(package.description)
        self.version = QLabel(package.version)
        self.uuid = package.uuid

        self.layout = QGridLayout(self)
        self.actions = []
        self.action_button = {}
        for action in package.actions:
            self.actions.append(action)
            self.action_button[action] = QPushButton(action)

        if type == "list":
            mini_layout = QHBoxLayout()
            mini_layout.addWidget(self.icon)
            mini_layout.addWidget(self.name)
            self.layout.addLayout(mini_layout, 0, 0)
            self.layout.addWidget(self.version, 0, 1)
            self.layout.addWidget(self.description, 0, 2)

            line = 0
            while line < len(self.actions):
                self.layout.addWidget(self.action_button[self.actions[line]], 1, line)
                line += 1

        else:
            self.setFixedWidth(200)
            self.setFixedHeight(200)
            self.description.setFixedWidth(self.width())
            mini_layout = QHBoxLayout()
            mini_layout.addWidget(self.icon)
            mini_layout.addWidget(self.name)

            self.layout.addWidget(self.icon, 0, 0)
            self.layout.addWidget(self.name, 1, 0)
            self.layout.addWidget(self.version, 1, 1)
            self.layout.addWidget(self.description, 2, 0)

            row = 0
            while row < len(self.actions):
                # self.layout.addWidget(self.action_button[self.actions[row]], row, 3)
                row += 1

        self.setLayout(self.layout)
        self.show()

        if "Install" in self.actions:
            self.action_button["Install"].clicked.connect(lambda: self.return_message(self.action_button["Install"], "Install"))
        if "Ask" in self.actions:
            self.action_button["Ask"].clicked.connect(lambda: self.return_message(self.action_button["Ask"], "Ask"))
        if "Update" in self.actions:
            self.action_button["Update"].clicked.connect(lambda: self.return_message(self.action_button["Update"], "Update"))
        if "Delete" in self.actions:
            self.action_button["Delete"].clicked.connect(lambda: self.return_message(self.action_button["Delete"], "Delete"))
        if "Launch" in self.actions:
            self.action_button["Launch"].clicked.connect(lambda: self.return_message(self.action_button["Launch"], "Launch"))

    def return_message(self, button, action):
        if action == "Install":
            button.setEnabled(False)
        elif action =="Delete":
            os.system("appwiz.cpl")
        self._message = """{"uuid": "%s", "action": "kioskinterface%s", "subaction": "%s"}"""% (self.uuid, \
                                                                                                 action, action)
        send_message_to_am(self._message)

    def getname(self):
        return self.name.text()

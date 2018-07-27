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
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QHBoxLayout
from models import send_message_to_am
from views.date_picker import DatePickerWidget
import os


class CustomPackageWidget(QWidget):
    """This class create specialized widget for the package list."""
    def __init__(self, package, type="grid", ref=None):
        """
        Initialize the list-element object
        Params:
            package: Package object is the package we want to represent into the UI.
            type: string used originally to generate to kind of displaying : grid or list
        """
        super().__init__()
        self.ref = ref
        self.package = package
        self.type = type
        self.icon = QLabel("")
        self._message = ""
        self.scheduler_wrapper = None

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
                row += 1

        self.setLayout(self.layout)
        self.show()

        if "Install" in self.actions:
            self.action_button["Install"].clicked.connect(
                lambda: self.return_message(self.action_button["Install"], "Install"))
        if "Ask" in self.actions:
            self.action_button["Ask"].clicked.connect(
                lambda: self.return_message(self.action_button["Ask"], "Ask"))
        if "Update" in self.actions:
            self.action_button["Update"].clicked.connect(
                lambda: self.return_message(self.action_button["Update"], "Update"))
        if "Delete" in self.actions:
            self.action_button["Delete"].clicked.connect(
                lambda: self.return_message(self.action_button["Delete"], "Delete"))
        if "Launch" in self.actions:
            self.action_button["Launch"].clicked.connect(
                lambda: self.return_message(self.action_button["Launch"], "Launch"))

    def return_message(self, button, action):
        """
        return_message method send a signal to the agent-machine when a button is clicked
        Params:
            button : QPushButton is a reference to the clicked button
            action: string added to the message sent to the agent-machine. The possibilities are:
                "Install" | "Delete" | "Launch" | "Ask" | "Update"
        """
        if action == "Install":
            self.scheduler_wrapper = DatePickerWidget(self, button)
            self.scheduler_wrapper.show()

        elif action == "Delete":
            os.system("appwiz.cpl")
        self._message = """{"uuid": "%s", "action": "kioskinterface%s", "subaction": "%s"}""" % (self.uuid, \
                                                                                                 action, action)
        send_message_to_am(self._message)

    def getname(self):
        """
        getname returns the name of the package
            return: string representing the name of the package
        """
        return self.name.text()

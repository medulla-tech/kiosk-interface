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
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QHBoxLayout, QProgressBar
from kiosk_interface.models import send_message_to_am
from kiosk_interface.views.date_picker import DatePickerWidget

import base64
import os
import subprocess


class CustomPackageWidget(QWidget):
    """This class create specialized widget for the package list."""
    def __init__(self, package, ref=None):
        """
        Initialize the list-element object
        Params:
            package: Package object is the package we want to represent into the UI.
            ref: is a reference to the root app
        """
        super().__init__()
        self.ref = ref
        self.package = package
        self.icon = QLabel("")
        self._message = ""
        self.scheduler_wrapper = None

        icon = QPixmap("datas/" + package.icon)
        icon = icon.scaled(24, 24)
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
            self.action_button[action] = QPushButton(action, self)

        layout_info = QHBoxLayout(self)
        layout_info.addWidget(self.icon)
        layout_info.addWidget(self.name)
        layout_info.addWidget(self.version)
        layout_info.addWidget(self.description)

        layout_action = QHBoxLayout(self)
        for action in self.actions:
            layout_action.addWidget(self.action_button[action])

        # Displays a progressbar only if the package has a status and a stat of progression
        if hasattr(package, "status") and hasattr(package, "stat"):
            self.statusbar = QProgressBar(self)
            self.statusbar.setMinimum(0)
            self.statusbar.setMaximum(100)

            self.statusbar.setValue(package.stat)

            # Enable / disable the button if the progressbar is not completed
            if 0 < self.statusbar.value() < 100:
                if package.status in self.action_button:
                    self.action_button[package.status].setEnabled(False)
                else:
                    pass
            else:
                self.statusbar.setVisible(False)
                if package.status in self.action_button:
                    self.action_button[package.status].setEnabled(True)
                else:
                    pass
            self.layout.addWidget(self.statusbar, 2, 0, 1, 1)

        self.layout.addLayout(layout_info, 0, 0, 1, 1)
        self.layout.addLayout(layout_action, 1, 0, 1, 1)
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
            self.scheduler_wrapper.has_to_send.connect(lambda: send_message_to_am(
                """{"uuid": "%s", "action":
                "kioskinterface%s", "subaction": "%s", "utcdatetime": "%s"}"""
                % (self.uuid, action, action, self.scheduler_wrapper.tuple_selected)))

        elif action == "Delete":
            self._message = """{"uuid": "%s", "action": "kioskinterface%s", "subaction": "%s"}""" % (self.uuid,
                                                                                                     action, action)
            send_message_to_am(self._message)

        elif action == "Launch":
            launcher=""
            try:
                launcher = base64.b64decode(self.package.launcher).decode("utf-8")
            except Exception as e:
                if hasattr(self.package, "launcher"):
                    launcher = self.package.launcher
                else:
                    self.package['action'].remove("Launch")
            finally:
                if os.path.isfile(launcher):
                    try:
                        subprocess.Popen(launcher)
                    except Exception as e:
                        send_message_to_am('{"action":"kioskLog","type":"error","message":"%s"}' % e)
                else:
                    send_message_to_am('{"action":"kioskLog","type":"error","message":"The file %s doesnt exists"}'
                                       % launcher)

    def getname(self):
        """
        getname returns the name of the package
            return: string representing the name of the package
        """
        return self.name.text()

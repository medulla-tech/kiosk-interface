#!/usr/bin/python3
# coding: utf-8
""" Define a partial view to display packages in the list"""
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

import re
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QProgressBar,
    QMessageBox,
)

try:
    from kiosk_interface.views.date_picker import DatePickerWidget
except BaseException:
    from views.date_picker import DatePickerWidget

import base64
import os
import subprocess
from datetime import datetime


class CustomPackageWidget(QWidget):
    """This class create specialized widget for the package list."""

    def __init__(self, app, package):
        """
        Initialize the list-element object
        Params:
            app: is a reference to the root app
            package: Package object is the package we want to represent into the UI.
        """
        super().__init__()
        self.app = app
        self.package = package
        self.icon = QLabel("", self)
        self._message = ""
        self.scheduler_wrapper = None

        self.name = QLabel(package["name"])

        if "icon" in package and package["icon"] != "kiosk.png":
            icon = QPixmap(os.path.join(self.app.datasdir, package["icon"]))
        else:
            icon_name = search_icon_by_name(package["name"])

            if icon_name is False:
                icon = QPixmap(os.path.join(self.app.datasdir,"kiosk.png"))
            else:
                icon = QPixmap(os.path.join(self.app.datasdir, icon_name))
        icon = icon.scaled(24, 24)
        self.icon.setPixmap(icon)

        if "description" in package:
            self.description = QLabel(package["description"], self)
        else:
            self.description = QLabel("")

        self.description.setWordWrap(True)

        if "version" in package:
            self.version = QLabel(package["version"], self)
        else:
            self.version = QLabel("")

        self.uuid = package["uuid"]

        self.actions = []
        self.action_button = {}

        if "action" in package:
            for action in package["action"]:
                if action == "Launch":
                    if "launcher" in package:
                        self.actions.append(action)
                        self.action_button[action] = QPushButton(action)
                    else:
                        pass
                else:
                    self.actions.append(action)
                    self.action_button[action] = QPushButton(action)

            self.layout = QGridLayout()

            layout_info = QHBoxLayout()
            layout_info.addWidget(self.icon)
            layout_info.addWidget(self.name)
            layout_info.addWidget(self.version)
            layout_info.addWidget(self.description)

            layout_action = QHBoxLayout()
            for action in self.actions:
                layout_action.addWidget(self.action_button[action])

        # Displays a progressbar only if the package has a status and a stat of
        # progression
        if "status" in package and "stat" in package:
            self.statusbar = QProgressBar()
            self.statusbar.setMinimum(0)
            self.statusbar.setMaximum(100)

            self.statusbar.setValue(package["stat"])

            # Enable / disable the button if the progressbar is not completed

            if "action" in package and package["status"] in package["action"]:
                if 0 < self.statusbar.value() < 100:
                    if package["status"] in self.action_button:
                        self.action_button[package["status"]].setEnabled(False)
                    else:
                        pass
                else:

                    if self.statusbar.value() == 100:

                        for pkg_ref in self.app.packages:
                            if pkg_ref == package:
                                pkg_ref["stat"] = 0

                    self.statusbar.setVisible(False)
                    if package["status"] in self.action_button:
                        self.action_button[package["status"]].setEnabled(True)
                    else:
                        pass
                self.layout.addWidget(self.statusbar, 2, 0, 1, 1)

        self.layout.addLayout(layout_info, 0, 0, 1, 1)
        self.layout.addLayout(layout_action, 1, 0, 1, 1)
        self.setLayout(self.layout)

        if "Install" in self.actions:
            self.action_button["Install"].clicked.connect(
                lambda: self.return_message(self.action_button["Install"], "Install")
            )
        if "Ask" in self.actions:
            self.action_button["Ask"].clicked.connect(
                lambda: self.return_message(self.action_button["Ask"], "Ask")
            )
        if "Update" in self.actions:
            self.action_button["Update"].clicked.connect(
                lambda: self.return_message(self.action_button["Update"], "Update")
            )
        if "Delete" in self.actions:
            self.action_button["Delete"].clicked.connect(
                lambda: self.return_message(self.action_button["Delete"], "Delete")
            )
        if "Launch" in self.actions:
            self.action_button["Launch"].clicked.connect(
                lambda: self.return_message(self.action_button["Launch"], "Launch")
            )

    def return_message(self, button, action):
        """
        return_message method send a signal to the agent-machine when a button is clicked
        Params:
            button : QPushButton is a reference to the clicked button
            action: string added to the message sent to the agent-machine. The possibilities are:
                "Install" | "Delete" | "Launch" | "Ask" | "Update"
        """
        if action == "Install":
            self.app.temp_inventory = self.app.last_inventory
            self.scheduler_wrapper = DatePickerWidget(self, button)
            self.scheduler_wrapper.show()
            self.scheduler_wrapper.has_to_send.connect(
                lambda: self.app.send(
                    """{"uuid": "%s", "action":
                "kioskinterface%s", "subaction": "%s", "utcdatetime": "%s"}"""
                    % (self.uuid, action, action, self.scheduler_wrapper.tuple_selected)
                )
            )
            msg = self.app.translate(
                "Action", "The application %s is being installed" % self.name.text()
            )
        elif action == "Delete":
            self.app.temp_inventory = self.app.last_inventory
            button.setEnabled(False)
            button.setText("Uninstall in progress ...")

            self._message = (
                """{"uuid": "%s", "action": "kioskinterface%s", "subaction": "%s"}"""
                % (self.uuid, action, action)
            )
            self.app.send(self._message)
            msg = self.app.translate(
                "Action", "The application %s is being uninstalled" % self.name.text()
            )

        elif action == "Launch":
            if "launcher" in self.package:
                try:
                    launcher = base64.b64decode(self.package["launcher"]).decode(
                        "utf-8"
                    )
                except BaseException:
                    launcher = self.package["launcher"]

                launcher = inject_env_into_str(launcher)
                if os.path.isfile(launcher):
                    subprocess.Popen(launcher)
                    msg = self.app.translate(
                        "Action", "The app %s is launched" % self.name.text()
                    )

            else:
                if "Launch" in self.package["action"]:
                    self.package["action"].remove("Launch")

        elif action == "Ask":
            self._message = (
                """{"uuid": "%s", "action": "kioskinterface%s", "subaction": "%s", "askuser":"%s", "askdate":"%s"}"""
                % (self.uuid, action, action, os.getlogin(), datetime.now())
            )
            self.app.send(self._message)
            msg = self.app.translate(
                "Action",
                "The access to the application %s is asked to admin" % self.name.text(),
            )

        elif action == "Update":
            self._message = (
                """{"uuid": "%s", "action": "kioskinterface%s", "subaction": "%s"}"""
                % (self.uuid, action, action)
            )
            self.app.send(self._message)
            msg = self.app.translate(
                "Action", "The application %s is updating" % self.name.text()
            )

        else:
            self._message = (
                """{"uuid": "%s", "action": "kioskinterface%s", "subaction": "%s"}"""
                % (self.uuid, action, action)
            )
            self.app.send(self._message)


def search_icon_by_name(name):
    """Search the icon by association with the package name

    Param:
        str : the name of the icon we are looking for
    Returns:
        str: if a name is found
        False if no name is found
    """
    prefix = name.split(".")[0]

    datas_dir = os.path.join(os.path.dirname(__file__), '..', "datas")
    icon_list = os.listdir(datas_dir)
    icon_list = [
        {"name": icon.split(".")[0], "ext": icon.split(".")[1]} for icon in icon_list
    ]

    # Research the prefix in name value of icon_list
    for icon in icon_list:
        if re.match(prefix.replace('+', '\+').replace('*', '\*'), icon["name"], re.I):
            return icon["name"] + "." + icon["ext"]
    return False


def inject_env_into_str(mesg):
    """Replace all the @_@variable@_@ by the env variable into the string.
    Param:
        str which contains the @_@variable@_@
    Returns:
        str with the env variables replaced
    """
    for t in re.findall("@_@.*?@_@", mesg):
        z = t.replace("@_@", "")
        try:
            mesg = mesg.replace(t, os.environ[z])
        except BaseException:
            pass
        print(mesg)
    return mesg

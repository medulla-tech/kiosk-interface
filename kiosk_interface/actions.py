#!/usr/bin/python3
# coding: utf-8
"""This module packs the actions launched when an event is triggered"""
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


import json


class EventController(object):
    """Bind events with actions"""

    def __init__(self, appObject):
        """Manage the connexion between signals and actions
        Param:
            appObject: Application, reference to the main app"""
        self.app = appObject

        self.app.notifier.app_launched.connect(self.action_app_launched)
        self.app.notifier.message_sent_to_am.connect(
            self.action_message_sent_to_am)
        self.app.notifier.server_cant_send_message_to_am.connect(
            self.action_server_cant_send_message_to_am)
        self.app.notifier.message_received_from_am.connect(
            self.action_message_received_from_am)
        self.app.notifier.tray_action_open.connect(
            self.action_tray_action_open)

    def action_message_received_from_am(self, message="{}"):
        """Action launched when the kiosk receive a message from Agent Master.
        Param:
            message: str this message is normally a json stringified. In function of the elements contained in the message,
            the action will reacts differently."""

        self.app.message = message
        self.app.logger(
            "info", self.app.translate(
                "Server", "Received message from AM"))
        if self.app.connected is False:
            self.app.connected = True
            self.app.notifier.server_status_changed.emit()

        print("message reçu :")
        print(message)
        try:
            decoded = json.loads(self.app.message)

            if "action" in decoded:
                if decoded["action"] == "packages" or decoded["action"] == "update_profile":
                    if "packages_list" in decoded:
                        self.app.packages = decoded["packages_list"]

                elif decoded["action"] == "update_launcher":

                    packages = self.app.packages
                    for package in packages:
                        if package['uuid'] == decoded['uuid']:
                            package['launcher'] = decoded['launcher']
                    self.app.packages = packages

                elif decoded["action"] == "presence":
                    # If the AM send a ping to the kiosk, it answers by a pong
                    if decoded["type"] == "ping":
                        self.app.connected = True
                        self.app.send_pong()

                elif decoded["action"] == "action_notification":
                    if self.app.kiosk.tab_notification is not None:
                        self.app.kiosk.tab_notification.add_notification(
                            decoded['data']["message"])
                    else:
                        print(decoded["message"])

                    if 'status' in decoded['data'] and 'stat' in decoded['data']:
                        uuid = decoded['data']['path'].split("/")
                        uuid = uuid[-1]

                        _package = {}
                        index = 0
                        for package in self.app.packages:
                            if package['uuid'] == uuid:
                                index = self.app.packages.index(package)
                                _package = package
                                _package['status'] = decoded['data']['status']
                                _package['stat'] = int(decoded['data']['stat'])

                        self.app.packages[index] = _package

                self.app.kiosk.tab_kiosk.search()
        except Exception as error:
            self.app.logger(
                "error", self.app.translate(
                    "Action", "Error when trying to load datas"))

    def action_app_launched(self):
        """Action launched when the kiosk is launched"""
        self.app.send(
            '{"action":"kioskinterface", "subaction":"initialization"}')
        self.app.logger(
            "info",
            self.app.translate(
                "Application",
                "Application launched"))

    def action_message_sent_to_am(self, message):
        """Action launched when a message is sent to the Agent Machine"""

        if self.app.connected is False:
            self.app.connected = True
            self.app.notifier.server_status_changed.emit()

    def action_server_cant_send_message_to_am(self, message):
        """Action launched when a message is received from the Agent Machine"""
        msg = self.app.translate("Server", "Message can't be sent to AM ")
        print(msg + ": %s" % message)

        if self.app.connected is True:
            self.app.connected = False
            self.app.notifier.server_status_changed.emit()

    # Launch the kiosk main window
    def action_tray_action_open(self, criterion):
        """Action launched when the open action is pressed in the tray menu"""
        self.app.logger(
            'info', self.app.translate(
                "Kiosk", "Initialize the kiosk main window"))
        self.app.send_ping()
        self.app.kiosk.tab_kiosk.input_search.setText(criterion)
        self.app.kiosk.tab_kiosk.search()
        self.app.kiosk.show()

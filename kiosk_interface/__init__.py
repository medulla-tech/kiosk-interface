#!/usr/bin/env python3
# coding: utf-8
"""This module launch the kiosk interface"""
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

from kiosk_interface.config import ConfParameter
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from kiosk_interface.tray import Tray
from kiosk_interface.kiosk import Kiosk
from kiosk_interface.notifier import Notifier
from kiosk_interface.actions import EventController
from kiosk_interface.server import MessengerToAM, MessengerFromAM
from PyQt5.QtCore import QCoreApplication


class Application(QApplication):
    """Generate the main app object"""

    def __init__(self):
        """Initialize the object"""

        super().__init__(sys.argv)  # Initialize the Qapplication

        # To add an event :
        # 1 - In Notifier create the signal
        # 2 - In EventController, connect it to the function to call. The function is defined below the
        # EventController constructor.
        # 3 - call my_signal.emit() at the position you want to declare the event
        # 4 - All the application is accessible from anywhere:
        #   self.app is a reference to the main app
        #   self.app.tray is a reference to the Tray
        #   self.app.kiosk is a reference to the Kiosk
        #   self.app.notifier is a reference to the Notifier
        #   self.app.eventCtrl is a reference to the EventController
        #   self.app.parameters is a reference to the Config

        # Notify the application when something is happening
        self.notifier = Notifier()
        # Action launched when the kiosk emit a notification
        self.eventCtrl = EventController(self)

        self.connected = False
        self.message = None  # Contains the last received message interpreted as dict
        self.packages = []  # Contains the packages of the application

        # Reference to a translate function
        self.translate = QCoreApplication.translate

        # Keep the config parameters in memory
        self.parameters = ConfParameter()

        # Socket server. It is always running. This module listen and wait the messages from AM
        self.receiver = MessengerFromAM(self)

        # Contains the tray app
        self.tray = Tray(self)
        self.logger('info', 'Initialization')
        # The mechanics are launched here
        self.notifier.app_launched.emit()

        self.setWindowIcon(QIcon("datas/kiosk.png"))
        self.setApplicationName("Kiosk")
        # When the window is closed, the process is not killed
        self.setQuitOnLastWindowClosed(False)

        # Contains the kiosk app
        self.kiosk = Kiosk(self)

    def run(self):

        self.exec()

    # Associate a unique sender. This module send messages to AM
    def send(self, message):
        messenger = MessengerToAM(self)
        messenger.send(message)

    def logger(self, type, msg):
        """Send log message to Agent Machine.
        Params:
            type: str corresponds to the type of log we want add to the xmpp logs. The types can be :
                - "info"
                - "error"
                - "debug"
            msg: str of the message we want add to log xmpp"""
        message = '{"action": "kioskLog","type": "%s", "message": "%s"}' % (type, self.translate("Log", msg))
        self.send(message)

    def send_ping(self):
        """Send a ping signal to the AM"""
        signal_presence = '{"action": "presence", "type":"ping"}'
        self.send(signal_presence)

    def send_pong(self):
        """Send a pong signal to the AM"""
        signal_presence = '{"action": "presence", "type":"pong"}'
        self.send(signal_presence)


if __name__ == "__main__":
    app = Application()
    app.send_ping()
    app.run()

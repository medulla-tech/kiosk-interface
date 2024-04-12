#!/usr/bin/python3
# coding: utf-8
"""This module launch the kiosk interface"""
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

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
import logging

try:
    # Import for unit tests
    from kiosk_interface.config import ConfParameter
    from kiosk_interface.tray import Tray
    from kiosk_interface.kiosk import Kiosk
    from kiosk_interface.notifier import Notifier
    from kiosk_interface.actions import EventController
    from kiosk_interface.server import MessengerToAM, MessengerFromAM
except BaseException:
    # Import for normal use
    from .config import ConfParameter
    from .tray import Tray
    from .kiosk import Kiosk
    from .notifier import Notifier
    from .actions import EventController
    from .server import MessengerToAM, MessengerFromAM


class Application(QApplication):
    """Generate the main app object"""

    def __init__(self, conf):
        """Initialize the object"""
        super().__init__(sys.argv)  # Initialize the Qapplication
        self.log = logging.getLogger()

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

        # Shortcuts to some working directories
        self.rootdir = os.path.dirname(__file__)
        self.datasdir = os.path.join(self.rootdir, "datas")
        self.viewsdir = os.path.join(self.rootdir, "views")

        # Notify the application when something is happening
        self.notifier = Notifier()
        # Action launched when the kiosk emit a notification
        self.eventCtrl = EventController(self)

        self.connected = False
        self.row_message = ""  # Contains the last received message interpreted as dict
        self.message = {}
        self.packages = []  # Contains the packages of the application

        # Reference to a translate function
        self.translate = QCoreApplication.translate

        # Keep the config parameters in memory
        self.parameters = conf

        # Socket server. It is always running. This module listen and wait the
        # messages from AM
        self.receiver = MessengerFromAM(self)

        self.logger("info", "Initialization")
        self.log.info("Kiosk initialization")
        # The mechanics are launched here
        self.notifier.app_launched.emit()

        self.setWindowIcon(QIcon(os.path.join(self.datasdir, "datas", "kiosk.png")))
        self.setApplicationName("Kiosk")
        # When the window is closed, the process is not killed
        self.setQuitOnLastWindowClosed(False)

        # Contains the tray app
        self.tray = Tray(self)

        # Contains the kiosk app
        self.kiosk = Kiosk(self)

        # Contains ref to independant windows
        self.independant = {}

    def run(self):
        """Launch the main loop"""
        try:
            self.exec()
        except Exception as err:
            self.log.error("Error during execution: %s" % err)

    # Associate a unique sender. This module send messages to AM
    def send(self, message):
        messenger = MessengerToAM(self)
        try:
            messenger.send(message)
        except Exception as err:
            self.log.error("Error during sending %s : %s" % (message, err))

    def logger(self, type, msg):
        """Send log message to Agent Machine.
        Params:
            type: str corresponds to the type of log we want add to the xmpp logs. The types can be :
                - "info"
                - "error"
                - "debug"
            msg: str of the message we want add to log xmpp"""
        message = '{"action": "kioskLog","type": "%s", "message": "%s"}' % (
            type,
            self.translate("Log", msg),
        )
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
    conf = ConfParameter()
    format = "%(asctime)s - %(levelname)s -(LAUNCHER)%(message)s"
    formatter = logging.Formatter(format)
    logdir = os.path.dirname(conf.logfilename())
    if os.path.isdir(logdir):
        os.makedirs(logdir, exist_ok=True)
    logging.basicConfig(level=conf.log_level, format=format, filename=conf.logfilename(), filemode="a")

    app = Application(conf)
    app.send_ping()
    app.run()

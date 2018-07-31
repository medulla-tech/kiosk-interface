#!/usr/bin/env python3
# coding: utf-8
"""Declare the Tray object"""
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

import sys

from PyQt5.QtWidgets import QWidget,QErrorMessage
from PyQt5.QtGui import QCursor
from kiosk import Kiosk
from server import get_datakiosk
from views.tray import tray_main_view
from PyQt5.QtCore import pyqtSignal
import threading
from server import MessengerToAM


class Tray(QWidget):
    """This class define the system tray object. This is the first controller called by the app."""

    updated = pyqtSignal(name="updated")

    def __init__(self, app):
        """Initialization of the TrayIcon"""
        super().__init__()
        self.criterion = ""
        self.main_window = None
        self.parent_app = app
        self.first_open = True
        self.tray = None

        # Call the view for the System Tray
        self.send('{"action":"kioskLog","type":"info","message":"Call the tray main view"}')
        tray_main_view(self)

        # Bind the actions
        self.tray.activated.connect(lambda: self.open_menu())  # left click action
        self.open_action.triggered.connect(self.open)

        if hasattr(self, 'input_search'):
            self.input_search.clicked.connect(self.criterion_modified)

    def open(self, criterion=""):
        """This method is called if the event 'open' is launched"""

        self.send('{"action":"kioskLog","type":"info",\
        "message":"Tray <open action> pressed : try to open the kiosk main window"}')

        datas = get_datakiosk()

        if datas is not None:
            self.send('{"action":"kioskLog","type":"info","message":"Initialize the kiosk main window"}')
            self.main_window = Kiosk(criterion, self.parent_app, self)

            if self.first_open is False:
                message = """{"action": "kioskinterface", "subaction": "initialization"}"""
                self.send(message)

            else:
                self.first_open = False
            self.main_window.resize(650, 550)
            self.send('{"action":"kioskLog","type":"info","message":"Calling the kiosk main view"}')
            self.main_window.show()
        else:
            self.main_window = QErrorMessage()
            self.main_window.showMessage("No data found")

    def criterion_modified(self):
        """This method is called when the search criterion is modified """
        self.send('{"action":"kioskLog","type":"info","message":"Set criterion to %s"}'%self.input_search.text)
        self.criterion = self.input_search.text()
        self.open(self.criterion)

    def send(self, message, parallel=True):
        """Send the specified message to the agent machine
                Params:
                    message: string which represent the commande launched into the agent machine.
                    parallel: boolean representing a flag if the message will be send un a thread or not
                """

        client = MessengerToAM()
        if parallel:
            thread = threading.Thread(target=client.send, args=(message.encode('utf-8'),))
            thread.start()
        else:
            client.send(message.encode('utf-8'))

    def open_menu(self):
        """Method used to open the menu from the tray with left click"""
        cursor = QCursor()
        self.menu.popup(cursor.pos())

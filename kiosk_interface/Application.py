#!/usr/bin/env python3
# coding: utf-8
"""This module generate the main app object"""
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

from config import ConfParameter
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import threading
import socket
from server import tcpserver
from tray import Tray
from server import MessengerToAM
from server import get_datakiosk, set_datakiosk
import logging

class Application(object):
    """This module generate the main app object"""
    parameters = ConfParameter()

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        """Initialize the object"""
        logging.info("Kiosk Initialization")
        self.app = None
        self.eventkill = None
        self.sock = None
        self.client_handlertcp = None
        self.tray = None

        logging.info("Call Application.init_app()")
        self.init_app()

    def init_app(self):
        """The mechanics are launched here"""
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon("datas/kiosk.png"))
        self.app.setApplicationName("Kiosk")

        message = """{"action": "kioskinterface", "subaction": "initialization"}"""
        logging.info("Call Application.send(%s)"% (message))
        self.send(message)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', 8766)

        logging.info('starting server tcp kiosk qt on %s port %s' % server_address)
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(5)
        self.eventkill = threading.Event()
        self.client_handlertcp = threading.Thread(target=tcpserver, args=(self.sock, self.eventkill,))
        # run server tcpserver for kiosk
        self.client_handlertcp.start()

        # When the window is closed, the process is not killed
        self.app.setQuitOnLastWindowClosed(False)

        logging.info("Call tray controller")
        self.tray = Tray(self)

        self.app.exec_()
        # using event eventkill for signal stop thread
        self.eventkill.set()
        self.sock.close()

        # connect server for pass accept for end
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = ('localhost', 8766)
        print('deconnecting to %s:%s' % server_address)
        self.sock.connect(server_address)
        self.sock.close()

    def send(self, message):
        """Send the specified message to the agent machine
        Params:
            message: string which represent the commande launched into the agent machine.
        """

        client = MessengerToAM()
        logging.info("Call client.send(%s)"%(message.encode('utf-8')))
        client.send(message.encode('utf-8'))
        get_datakiosk()

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
from notifier import Notifier


class Application(object):
    """This module generate the main app object"""
    parameters = ConfParameter()

    def __init__(self):
        """Initialize the object"""
        self.notifier = None
        self.app = None
        self.send("""{"action": "kioskLog","type":"info","message":"Kiosk Initialization"}""")
        self.eventkill = None
        self.sock = None
        self.client_handlertcp = None
        self.tray = None
        self.send('{"action": "kioskLog", "type": "info", "message": "Call Application init method"}')
        self.init_app()

    def init_app(self):
        """The mechanics are launched here"""
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon("datas/kiosk.png"))
        self.app.setApplicationName("Kiosk")

        self.notifier = Notifier()
        message = '{"action": "kioskinterface", "subaction": "initialization"}'
        self.send(message, parallel=False)
        self.send('{"action":"kioskLog","type":"info","message":"Call Application.send function"}')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', 8766)

        self.send('{"action": "kioskLog", "type": "info",\
        "message": "starting server tcp kiosk qt on %s port %s"}' %server_address)
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(5)
        self.eventkill = threading.Event()
        self.client_handlertcp = threading.Thread(target=tcpserver, args=(self, self.sock, self.eventkill,))
        # run server tcpserver for kiosk
        self.client_handlertcp.start()

        # When the window is closed, the process is not killed
        self.app.setQuitOnLastWindowClosed(False)

        # Notifications
        self.notifier.message_sent_to_am.connect(lambda:print("message sent"))
        self.notifier.message_update_received_from_am.connect(lambda:print("update received"))
        self.notifier.message_received_from_am.connect(lambda:print("message received"))
        self.send('{"action":"kioskLog", "type":"info", "message":"Call tray controller"}')
        self.tray = Tray(self)


        self.app.exec_()
        # using event eventkill for signal stop thread
        self.eventkill.set()
        self.sock.close()

        # connect server for pass accept for end
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = ('localhost', 8766)
        self.send('{"action":"kioskLog", "type":"info", "message":"deconnecting to %s:%s"}' % server_address)
        self.sock.connect(server_address)
        self.sock.close()

    def send(self, message, parallel=True):
        """Send the specified message to the agent machine
                Params:
                    message: string which represent the commande launched into the agent machine.
                    parallel: boolean representing a flag if the message will be send in a thread or not
                """
        if self.notifier is not None:
            self.notifier.message_sent_to_am.emit()
        client = MessengerToAM()
        if parallel:
            thread = threading.Thread(target=client.send, args=(message.encode('utf-8'),))
            thread.start()
        else:
            client.send(message.encode('utf-8'))

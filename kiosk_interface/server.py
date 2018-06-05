#!/usr/bin/env python3
# coding: utf-8
"""Manage the configuration of the kiosk"""
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
import threading
import socket
import json
from config import ConfParameter

global datakiosk

def get_datakiosk():
    global datakiosk
    return datakiosk

def set_datakiosk(data):
    global datakiosk
    datakiosk = data


    
def tcpserver(sock, eventkill):
        """
        this function is the listening function of the tcp server of the machine agent, to serve the request of the kiosk
        Args:
            no arguments

        Returns:
            no return value
        """
        print("Server Kiosk Start")
        while not eventkill.wait(1):
            # Wait for a connection
            print('waiting for a connection kiosk service')
            connection, client_address = sock.accept()
            client_handler = threading.Thread(
                                                target=handle_client_connection,
                                                args=(connection,))
            client_handler.start()
        print("Stopping Kiosk")


def handle_client_connection(client_socket):
    """
        this function handles the message received from kiosk
        the function must provide a response to an acknowledgment kiosk or a result
        Args:
            client_socket: socket for exchanges between AM and Kiosk

        Returns:
            no return value
    """
    try:
        # request the recv message
        recv_msg_from_AM = client_socket.recv(5000)
        recv_msg_from_AM = recv_msg_from_AM.decode("utf-8")
        print (recv_msg_from_AM)
        print ("initialise la data")
        set_datakiosk(json.loads(recv_msg_from_AM))
        print (get_datakiosk())
        client_socket.send(recv_msg_from_AM.encode("utf-8"))
    finally:
        client_socket.close()


class MessengerToAM(object):
    def __init__(self):
        """Initialization of the MessagerToAM object"""

        parameters = ConfParameter()
        # Next we create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (parameters.am_server, parameters.am_local_port)
        self.active = False

        try:
            self.sock.connect(server_address)
            self.active = True
        except socket.error:
            self.active = False
            print("The communication with the agent machine can't be established")

    def send(self, msg):
        """Send the specified message to the agent machine.
        Args:
            msg: str of the message sent to the agent machine. This message must has the following structure:
            '{"uuid" : "45d4-3124c21-3123", "action": "kioskinterfaceinstall", "subaction" : "install"}'
        """
        if self.active:
            print('msg = '+str(msg))
            self.sock.sendall(msg)
            self.handle()
        else:
            self.sock.close()

    def handle(self):
        """The handle allow the agent machine to return back a response to the kiosk-interface.
        The datas returned back by the agent machine are returned by this function.

        Returns:
            str: The return back message
        """
        data = self.sock.recv(1024).strip()
        print('received "%s"' % data)
        self.sock.close()
        return data
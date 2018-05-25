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
        recv_msg_from_kiosk = client_socket.recv(1024)
        # print 'Received {}'.format(recv_msg_from_kiosk)
        # send result or acquit
        client_socket.send(recv_msg_from_kiosk)
    finally:
        client_socket.close()


        

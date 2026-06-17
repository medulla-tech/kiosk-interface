#!/usr/bin/python3
# coding: utf-8
"""Manage the communication between the kiosk and the agent machine."""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

import threading
import socket
import json


class MessengerFromAM(object):
    def __init__(self, appObject):
        self.app = appObject
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (
            self.app.parameters.am_server,
            self.app.parameters.kiosk_local_port,
        )
        self.sock.bind(self.server_address)
        self.sock.listen(5)
        self.eventkill = threading.Event()
        self.client_handlertcp = threading.Thread(
            target=self.tcpserver,
            args=(
                self.app,
                self.sock,
                self.eventkill,
            ),
        )
        # run server tcpserver for kiosk
        self.client_handlertcp.start()

    def tcpserver(self, ref, sock, eventkill):
        """
        This function is the listening function of the tcp server of the machine agent, to serve the request of the kiosk
        Params:
            sock socket object which receives the message form agent-machine
            eventkill threading event object used to signal the end of the standby
        """
        while not eventkill.wait(1):
            # Wait for a connection
            connection, client_address = sock.accept()
            client_handler = threading.Thread(
                target=self.handle_client_connection,
                args=(
                    ref,
                    connection,
                ),
            )
            client_handler.start()

    def handle_client_connection(self, ref, client_socket):
        """
        this function handles the message received from kiosk
        the function must provide a response to an acknowledgment kiosk or a result
        Args:
            client_socket: socket for exchanges between AM and Kiosk

        Returns:
            no return value
        """
        recv_msg_from_AM = b""
        try:
            # Read until the full message arrives: a single recv() can truncate
            # a large package list (TCP is a stream) -> JSON error + RST. Loop
            # until the buffer parses as complete JSON (or peer close / timeout).
            client_socket.settimeout(5)
            chunks = []
            while True:
                try:
                    chunk = client_socket.recv(8192)
                except Exception:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
                try:
                    json.loads(b"".join(chunks).decode("utf-8"))
                    break  # complete JSON received, stop reading
                except (ValueError, UnicodeDecodeError):
                    continue  # message not complete yet, keep reading
            recv_msg_from_AM = b"".join(chunks)
            try:
                recv_msg_from_AM = recv_msg_from_AM.decode("utf-8")
            except:
                pass
            ref.message = recv_msg_from_AM
            ref.notifier.message_received_from_am.emit(recv_msg_from_AM)

        finally:
            ref.log.info("recieved from AM: %s" % recv_msg_from_AM)
            client_socket.close()


class MessengerToAM(object):
    """MessengerToAM is a client socket class"""

    def __init__(self, appObject):
        """Initialization of the MessagerToAM object"""

        self.app = appObject
        # Next we create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (
            self.app.parameters.am_server,
            self.app.parameters.am_local_port,
        )
        self.active = False

        try:
            self.sock.connect(server_address)
            self.active = True
        except socket.error:
            self.active = False

    def send(self, msg):
        """Send the specified message to the agent machine.
        Args:
            msg: str of the message sent to the agent machine. This message must has the following structure:
            '{"uuid" : "45d4-3124c21-3123", "action": "kioskinterfaceinstall", "subaction" : "install"}'
        """
        if self.active:
            self.app.log.info("send datas to AM : %s"%msg)
            if not isinstance(msg, bytes):
                self.sock.sendall(msg.encode("utf-8"))
                self.app.notifier.message_sent_to_am.emit(msg)
            else:
                self.sock.sendall(msg)
                self.app.notifier.message_sent_to_am.emit(msg.decode("utf-8"))
            self.handle()
        else:
            self.app.notifier.server_cant_send_message_to_am.emit(msg)
            self.sock.close()

    def handle(self):
        """The handle allow the agent machine to return back a response to the kiosk-interface.
        The datas returned back by the agent machine are returned by this function.

        Returns:
            str: The return back message
        """
        data = self.sock.recv(1024).strip()
        self.sock.close()
        return data

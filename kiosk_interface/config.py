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
import sys

import os
import configparser
import socket

def conffilename(agenttype):
    """
        Function defining where the configuration file is located.
        configuration file for the type of machifne and the Operating System

        Args:
        agenttype: type of the agent, relay or machine or (cluster for ARS)

        Returns:
        Return the config file path

    """
    if agenttype in ["machine"]:
        conffilenameparameter = "agentconf.ini"
    elif agenttype in ["cluster"]:
        conffilenameparameter = "cluster.ini"
    else:
        conffilenameparameter = "relayconf.ini"
    if sys.platform.startswith('linux'):
        fileconf = os.path.join(
            "/",
            "etc",
            "pulse-xmpp-agent",
            conffilenameparameter)
    elif sys.platform.startswith('win'):
        fileconf = os.path.join(
            os.environ["ProgramFiles"],
            "Pulse",
            "etc",
            conffilenameparameter)
    elif sys.platform.startswith('darwin'):
        fileconf = os.path.join(
            "/",
            "Library",
            "Application Support",
            "Pulse",
            "etc",
            conffilenameparameter)
    else:
        fileconf = conffilenameparameter
    if conffilenameparameter == "cluster.ini":
        return fileconf
    if os.path.isfile(fileconf):
        return fileconf
    else:
        return conffilenameparameter


class ConfParameter:
    """ConfParameter create an interface to make easier the use of config files."""
    def __init__(self, typeconf='machine'):
        """Initialization of ConfParameter object """
        config = configparser.ConfigParser()
        namefileconfig = conffilename(typeconf)
        config.read(namefileconfig)
        if os.path.exists(namefileconfig + ".local"):
            config.read(namefileconfig + ".local")
        self.packageserver = {}

        # Default parameters if no conf is found
        self.am_local_port = 8765
        self.kiosk_local_port = 8766
        self.am_server = "localhost"

        # Set these attribute with config element found
        if config.has_option('kiosk', 'am_local_port'):
            self.am_local_port = config.getint('kiosk', 'am_local_port')
        if config.has_option('kiosk', 'kiosk_local_port'):
            self.kiosk_local_port = config.getint('kiosk', 'kiosk_local_port')
        if config.has_option('kiosk', 'am_server'):
            self.am_server = config.get('kiosk', 'am_server')


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

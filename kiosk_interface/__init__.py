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

import sys
from PyQt5.QtWidgets import QApplication
from tray import Tray
from config import ConfParameter
import socket
from server import tcpserver
import threading
from server import set_datakiosk


set_datakiosk(None)

parameters = ConfParameter()
##print (parameters.am_local_ports)


    
app = QApplication(sys.argv)
app.setApplicationName("Kiosk")

eventkill = threading.Event()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('localhost',  8766)
print ('starting server tcp kiosk qt on %s port %s' % server_address)
sock.bind(server_address)
# Listen for incoming connections
sock.listen(5)


client_handlertcp = threading.Thread(target=tcpserver, args=(sock,eventkill,))
# run server tcpserver for kiosk 
client_handlertcp.start()


        
# When the window is closed, the process is not killed
app.setQuitOnLastWindowClosed(False)

tray = Tray()

app.exec_()
#using event eventkill for signal stop thread
eventkill.set()
sock.close()

#connect server for pass accept for end
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('localhost', 8766)
print( 'deconnecting to %s:%s' % server_address)
sock.connect(server_address)
sock.close()


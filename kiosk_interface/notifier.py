#!/usr/bin/env python3
# coding: utf-8
"""Declare some notifier for the app"""
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

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import pyqtSignal


class Notifier(QWidget):
    """This class allows to create some signals for the application"""
    app_launched = pyqtSignal()
    app_claused = pyqtSignal()

    tray_loaded = pyqtSignal()
    tray_action_open = pyqtSignal((str,))

    kiosk_loaded = pyqtSignal()

    server_tcp_start = pyqtSignal()
    server_tcp_stop = pyqtSignal()
    server_cant_send_message_to_am = pyqtSignal((str,))
    server_ping_presence = pyqtSignal()

    message_received_from_am = pyqtSignal((str,))
    message_sent_to_am = pyqtSignal((str,))

    updated = pyqtSignal((str,dict,))

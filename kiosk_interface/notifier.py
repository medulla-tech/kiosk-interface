#!/usr/bin/python3
# coding: utf-8
"""Declare some notifier for the app"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal


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
    server_status_changed = pyqtSignal()
    message_received_from_am = pyqtSignal((str,))
    message_sent_to_am = pyqtSignal((str,))

    updated = pyqtSignal(
        (
            str,
            dict,
        )
    )

    toaster_new_update = pyqtSignal((dict,))

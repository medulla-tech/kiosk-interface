#!/usr/bin/python3
# coding: utf-8
"""Test the notifier module"""
#
# (c) 2018-2022 Siveo, http://www.siveo.net
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

from PyQt5.QtCore import pyqtSignal

from kiosk_interface.notifier import Notifier
from PyQt5.QtWidgets import QApplication
import PyQt5
import sys


class TestNotifier:
    """Test the notifier module"""

    app = QApplication(sys.argv)
    notifier = Notifier()

    def test_init(self):
        assert self.notifier is not None
        assert isinstance(self.notifier, Notifier)

    def test_existing_signals(self):
        assert hasattr(self.notifier, "app_launched")
        assert hasattr(self.notifier, "app_claused")
        assert hasattr(self.notifier, "tray_loaded")
        assert hasattr(self.notifier, "tray_action_open")
        assert hasattr(self.notifier, "kiosk_loaded")
        assert hasattr(self.notifier, "server_tcp_start")
        assert hasattr(self.notifier, "server_tcp_start")
        assert hasattr(self.notifier, "server_tcp_stop")
        assert hasattr(self.notifier, "server_cant_send_message_to_am")
        assert hasattr(self.notifier, "server_ping_presence")
        assert hasattr(self.notifier, "server_status_changed")
        assert hasattr(self.notifier, "message_received_from_am")
        assert hasattr(self.notifier, "message_sent_to_am")
        assert hasattr(self.notifier, "updated")

    def test_type_signals(self):
        assert isinstance(self.notifier.app_launched, PyQt5.QtCore.pyqtBoundSignal)
        assert isinstance(self.notifier.app_claused, PyQt5.QtCore.pyqtBoundSignal)
        assert isinstance(self.notifier.tray_loaded, PyQt5.QtCore.pyqtBoundSignal)
        assert isinstance(self.notifier.tray_action_open, PyQt5.QtCore.pyqtBoundSignal)
        assert isinstance(self.notifier.kiosk_loaded, PyQt5.QtCore.pyqtBoundSignal)
        assert isinstance(self.notifier.server_tcp_start, PyQt5.QtCore.pyqtBoundSignal)
        assert isinstance(self.notifier.server_tcp_stop, PyQt5.QtCore.pyqtBoundSignal)
        assert isinstance(
            self.notifier.server_cant_send_message_to_am, PyQt5.QtCore.pyqtBoundSignal
        )
        assert isinstance(
            self.notifier.server_ping_presence, PyQt5.QtCore.pyqtBoundSignal
        )
        assert isinstance(
            self.notifier.server_status_changed, PyQt5.QtCore.pyqtBoundSignal
        )
        assert isinstance(
            self.notifier.message_received_from_am, PyQt5.QtCore.pyqtBoundSignal
        )
        assert isinstance(
            self.notifier.message_sent_to_am, PyQt5.QtCore.pyqtBoundSignal
        )
        assert isinstance(self.notifier.updated, PyQt5.QtCore.pyqtBoundSignal)

    def test_connect_signals(self):
        def _action_app_launched():
            assert True

        def _action_app_claused():
            assert True

        def _action_tray_loaded():
            assert True

        def _action_tray_action_open(msg):
            assert msg == "string"

        def _action_kiosk_loaded():
            assert True

        def _action_server_tcp_start():
            assert True

        def _action_server_tcp_stop():
            assert True

        def _action_server_cant_send_message_to_am(msg):
            assert msg == "string"

        def _action_server_ping_presence():
            assert True

        def _action_server_status_changed():
            assert True

        def _action_message_received_from_am(msg):
            assert msg == "string"

        def _action_message_sent_to_am(msg):
            assert msg == "string"

        def _action_updated(msg, dict):
            assert msg == "string"
            assert dict == {"dict": True, "key": "value"}

        self.notifier.app_launched.connect(_action_app_launched)
        self.notifier.app_claused.connect(_action_app_claused)
        self.notifier.tray_loaded.connect(_action_tray_loaded)
        self.notifier.tray_action_open.connect(_action_tray_action_open)
        self.notifier.kiosk_loaded.connect(_action_kiosk_loaded)
        self.notifier.server_tcp_start.connect(_action_server_tcp_start)
        self.notifier.server_tcp_stop.connect(_action_server_tcp_stop)
        self.notifier.server_cant_send_message_to_am.connect(
            _action_server_cant_send_message_to_am
        )
        self.notifier.server_ping_presence.connect(_action_server_ping_presence)
        self.notifier.server_status_changed.connect(_action_server_status_changed)
        self.notifier.message_received_from_am.connect(_action_message_received_from_am)
        self.notifier.message_sent_to_am.connect(_action_message_sent_to_am)
        self.notifier.updated.connect(_action_updated)

    def test_emit_signals(self):
        assert self.notifier.app_launched.emit() is None
        assert self.notifier.app_claused.emit() is None
        assert self.notifier.tray_loaded.emit() is None
        assert self.notifier.tray_action_open.emit("string") is None
        assert self.notifier.kiosk_loaded.emit() is None
        assert self.notifier.server_tcp_start.emit() is None
        assert self.notifier.server_tcp_stop.emit() is None
        assert self.notifier.server_cant_send_message_to_am.emit("string") is None
        assert self.notifier.server_ping_presence.emit() is None
        assert self.notifier.server_status_changed.emit() is None
        assert self.notifier.message_received_from_am.emit("string") is None
        assert self.notifier.message_sent_to_am.emit("string") is None
        assert (
            self.notifier.updated.emit("string", {"dict": True, "key": "value"}) is None
        )

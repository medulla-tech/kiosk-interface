#!/usr/bin/env python3
# coding: utf-8
"""Test the config module"""
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

from kiosk_interface import ConfParameter
from kiosk_interface.config import conffilename
import sys
import os


def test_config_file():
    """Test the config file path function"""
    if sys.platform.startswith('win'):
        assert conffilename("machine") == "C:\\Program Files\\Pulse\\etc\\agentconf.ini"
        assert conffilename("cluster") == "C:\\Program Files\\Pulse\\etc\\cluster.ini"
        if os.path.isfile("C:\\Program Files\\Pulse\\etc\\relayconf.ini"):
            assert conffilename("") == "C:\\Program Files\\Pulse\\etc\\relayconf.ini"
        else:
            assert conffilename("") == "relayconf.ini"

    elif sys.platform.startswith('linux'):
        assert conffilename("machine") == "/etc/pulse-xmpp-agent/agentconf.ini"
        assert conffilename("cluster") == "/etc/pulse-xmpp-agent/cluster.ini"
        if os.path.isfile("/etc/pulse-xmpp-agent/relayconf.ini"):
            assert conffilename("") == "/etc/pulse-xmpp-agent/relayconf.ini"
        else:
            assert conffilename("") == "relayconf.ini"

    elif sys.platform.startswith("darwin"):
        assert conffilename("machine") == "agentconf.ini"
        assert conffilename("cluster") == "/Library/Application Support/Pulse/etc/cluster.ini"
        if os.path.isfile("/Library/Application Support/Pulse/etc/relayconf.ini"):
            assert conffilename("") == "/Library/Application Support/Pulse/etc/relayconf.ini"
        else:
            assert conffilename("") == "relayconf.ini"


class TestConfig():
    """Test the config module"""
    conf = ConfParameter()

    def test_init(self):
        """Test the ConfigParameter creation"""
        assert self.conf is not None
        assert type(self.conf) is ConfParameter

    def test_attr(self):
        """Test the attributes of ConfigParameter class"""
        assert hasattr(self.conf, "am_local_port") is True
        assert self.conf.am_local_port is not None
        assert self.conf.am_local_port == 8765

        assert hasattr(self.conf, "kiosk_local_port") is True
        assert self.conf.kiosk_local_port is not None
        assert self.conf.kiosk_local_port == 8766

        assert hasattr(self.conf, "am_server") is True
        assert self.conf.am_local_port is not None
        assert self.conf.am_server == "localhost" or "127.0.0.1"

        assert hasattr(self.conf, "width") is True
        assert self.conf.width is not None
        assert self.conf.width == 650

        assert hasattr(self.conf, "height") is True
        assert self.conf.height is not None
        assert self.conf.height == 550

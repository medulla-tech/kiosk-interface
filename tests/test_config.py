#!/usr/bin/python3
# coding: utf-8
"""Test the config module"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from kiosk_interface import ConfParameter
from kiosk_interface.config import conffilename
import sys
import os


def test_config_file():
    """Test the config file path function"""
    if sys.platform.startswith("win"):
        assert conffilename("machine") == "C:\\Program Files\\Medulla\\etc\\agentconf.ini"
        assert conffilename("cluster") == "C:\\Program Files\\Medulla\\etc\\cluster.ini"
        if os.path.isfile("C:\\Program Files\\Medulla\\etc\\relayconf.ini"):
            assert conffilename("") == "C:\\Program Files\\Medulla\\etc\\relayconf.ini"
        else:
            assert conffilename("") == "relayconf.ini"

    elif sys.platform.startswith("linux"):
        assert conffilename("machine") == "/etc/pulse-xmpp-agent/agentconf.ini"
        assert conffilename("cluster") == "/etc/pulse-xmpp-agent/cluster.ini"
        if os.path.isfile("/etc/pulse-xmpp-agent/relayconf.ini"):
            assert conffilename("") == "/etc/pulse-xmpp-agent/relayconf.ini"
        else:
            assert conffilename("") == "relayconf.ini"

    elif sys.platform.startswith("darwin"):
        assert conffilename("machine") == "agentconf.ini"
        assert (
            conffilename("cluster")
            == "/Library/Application Support/Pulse/etc/cluster.ini"
        )
        if os.path.isfile("/Library/Application Support/Pulse/etc/relayconf.ini"):
            assert (
                conffilename("")
                == "/Library/Application Support/Pulse/etc/relayconf.ini"
            )
        else:
            assert conffilename("") == "relayconf.ini"


class TestConfig:
    """Test the config module"""

    conf = ConfParameter()

    def test_init(self):
        """Test the ConfigParameter creation"""
        assert self.conf is not None
        assert isinstance(self.conf, ConfParameter)

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

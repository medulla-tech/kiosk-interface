#!/usr/bin/python3
# coding: utf-8
"""Manage the configuration of the kiosk"""
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
import sys

import os
import configparser


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
    if sys.platform.startswith("linux"):
        fileconf = os.path.join("/", "etc", "pulse-xmpp-agent", conffilenameparameter)
    elif sys.platform.startswith("win"):
        fileconf = os.path.join(
            os.environ["ProgramFiles"], "Pulse", "etc", conffilenameparameter
        )
    elif sys.platform.startswith("darwin"):
        fileconf = os.path.join(
            "/", "Library", "Application Support", "Pulse", "etc", conffilenameparameter
        )
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

    def __init__(self, typeconf="machine"):
        """
        Initialization of ConfParameter object
        Param:
            typeconf: string representing the type of the machine
        """
        config = configparser.ConfigParser()
        namefileconfig = conffilename(typeconf)
        config.read(namefileconfig)
        if os.path.exists(namefileconfig + ".local"):
            config.read(namefileconfig + ".local")

        # Default parameters if no conf is found
        self.am_local_port = 8765
        self.kiosk_local_port = 8766
        self.am_server = "localhost"

        # Set these attribute with config element found
        if config.has_option("kiosk", "am_local_port"):
            self.am_local_port = config.getint("kiosk", "am_local_port")
        if config.has_option("kiosk", "kiosk_local_port"):
            self.kiosk_local_port = config.getint("kiosk", "kiosk_local_port")
        if config.has_option("kiosk", "am_server"):
            self.am_server = config.get("kiosk", "am_server")

        self.width = 650
        self.height = 550

        self.log_level = self.get_loglevel_from_str("INFO")
        if config.has_option("global", "log_level"):
            self.log_level = self.get_loglevel_from_str(config.get("global", "log_level"))


    def get_loglevel_from_str(self, levelstring):
        strlevel = levelstring.upper()
        if strlevel in ["CRITICAL", "FATAL"]:
            return 50
        elif strlevel == "ERROR":
            return 40
        elif strlevel in ["WARNING", "WARN"]:
            return 30
        elif strlevel == "INFO":
            return 20
        elif strlevel == "DEBUG":
            return 10
        elif strlevel == "NOTSET":
            return 0
        elif strlevel in ["LOG", "DEBUGPULSE"]:
            return 25
        else:
            return 20

    def logfilename(self):
        """
        Function defining where the log file is located.
        configuration file for the type of machifne and the Operating System

        Returns:
        Return the log file path

        """
        logfilenameparameter = "kiosk-interface.log"

        if sys.platform.startswith("linux"):
            fileconf = os.path.join(os.path.expanduser("~"), logfilenameparameter)
        elif sys.platform.startswith("win"):
            fileconf = os.path.join(
                os.path.expanduser("~"), logfilenameparameter
            )
        elif sys.platform.startswith("darwin"):
            fileconf = os.path.join(os.path.expanduser("~"), logfilenameparameter)
        return fileconf

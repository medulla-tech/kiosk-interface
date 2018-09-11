#!/usr/bin/env python3
# coding: utf-8
""" Define the views for the Tray object"""
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

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QWidgetAction
from kiosk_interface.views.custom_search_bar import CustomSearchBar


def tray_main_view(ref):
    """
    This function generate the view for the system tray

    args:
        ref is the reference for the KioskMainWindow object
    """

    # Create the tray
    ref.icon = QIcon("datas/kiosk.png")
    ref.tray = QSystemTrayIcon(ref)
    ref.setWindowTitle(QCoreApplication.translate("TrayIcon", "Kiosk"))
    ref.tray.setToolTip(QCoreApplication.translate("TrayIcon", "Kiosk"))
    ref.tray.setIcon(ref.icon)
    # With this the kiosk is always running even if the main window is closed.
    ref.tray.setVisible(True)

    ref.menu = QMenu(ref)

    # The searchbar is not added if the kiosk is running on mac
    if sys.platform != "darwin":
        ref.search_action = QWidgetAction(ref)

        ref.input_search = CustomSearchBar()
        ref.search_action.setDefaultWidget(ref.input_search)

    # Add the open option to the menu
    ref.open_action = QAction(QCoreApplication.translate("TrayIcon", "Open"))
    if hasattr(ref, 'search_action'):
        ref.menu.addAction(ref.search_action)
    ref.menu.addAction(ref.open_action)

    # Add the menu to the tray
    ref.tray.setContextMenu(ref.menu)

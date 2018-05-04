#!/usr/bin/env python3
# coding: utf-8
""" Define the views for the Kiosk object"""
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
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QLineEdit, QGridLayout, QPushButton, \
    QListWidget


def kiosk_main_view(ref):
    """
    Define the main view for the kiosk window.
    param:
        ref is a reference to the Kiosk object
    """
    ref.setWindowTitle("Kiosk")

    ref.setLayout(QVBoxLayout(ref))
    # Tabs for differents kind of view
    ref.tabs = QTabWidget()
    ref.tabs.resize(600, 400)

    ref.tabs_content = [QWidget(), QWidget()]
    ref.tabs.addTab(ref.tabs_content[0], "Grid")
    ref.tabs.addTab(ref.tabs_content[1], "List")

    grid_content(ref)
    list_content(ref)

    ref.layout().addWidget(QLineEdit(ref))
    ref.layout().addWidget(ref.tabs)


def grid_content(ref):
    """
    Define the view for the tab 'grid' in the main window.
    param:
        ref is a reference to the Kiosk object
    """
    ref.tabs_content[0].layout = QGridLayout(ref)
    # ref.tabs_content[0].layout.setColumnStretch(0, 0)

    ref.tabs_content[0].layout.addWidget(QPushButton('1'), 0, 0)
    ref.tabs_content[0].layout.addWidget(QPushButton('2'), 0, 1)
    ref.tabs_content[0].layout.addWidget(QPushButton('3'), 0, 2)
    ref.tabs_content[0].layout.addWidget(QPushButton('4'), 1, 0)
    ref.tabs_content[0].layout.addWidget(QPushButton('5'), 1, 1)
    ref.tabs_content[0].layout.addWidget(QPushButton('6'), 1, 2)
    ref.tabs_content[0].layout.addWidget(QPushButton('7'), 2, 0)
    ref.tabs_content[0].layout.addWidget(QPushButton('8'), 2, 1)
    ref.tabs_content[0].layout.addWidget(QPushButton('9'), 2, 2)
    ref.tabs_content[0].setLayout(ref.tabs_content[0].layout)


def list_content(ref):
    """
        Define the view for the tab 'list' in the main window.
        param:
            ref is a reference to the Kiosk object
        """
    ref.tabs_content[1].layout = QVBoxLayout(ref.tabs)
    # ref.content_scroll = QScrollArea(ref.tabs_content[1])
    ref.list = QListWidget(ref.tabs_content[1])
    # ref.tabs_content[1].layout.addWidget(ref.content_scroll)
    ref.tabs_content[1].layout.addWidget(ref.list)

    ref.list.adjustSize()
    ref.list.addItems(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'])

    ref.tabs_content[1].setLayout(ref.tabs_content[1].layout)

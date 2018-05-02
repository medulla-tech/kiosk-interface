#!/usr/bin/env python3
# coding: utf-8
#
# (c) 2018 siveo, http://www.siveo.net
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
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class KioskMainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(600,400)
        self.setWindowTitle("Kiosk")

        # Tabs for differents kind of view
        self.tabs = QTabBar(self)



        #self.horizontalGroupBox = QGroupBox(self)
        self.layout = QGridLayout(self)
        self.layout.setColumnStretch(0, 0)

        self.layout.addWidget(QPushButton('1'), 0, 0)
        self.layout.addWidget(QPushButton('2'), 0, 1)
        self.layout.addWidget(QPushButton('3'), 0, 2)
        self.layout.addWidget(QPushButton('4'), 1, 0)
        self.layout.addWidget(QPushButton('5'), 1, 1)
        self.layout.addWidget(QPushButton('6'), 1, 2)
        self.layout.addWidget(QPushButton('7'), 2, 0)
        self.layout.addWidget(QPushButton('8'), 2, 1)
        self.layout.addWidget(QPushButton('9'), 2, 2)

        #self.horizontalGroupBox.setLayout(layout)

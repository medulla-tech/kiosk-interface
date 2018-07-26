#!/usr/bin/env python3
# coding: utf-8
""" Define the view for the datepicker widget when we click on install button"""
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

from PyQt5.QtWidgets import QWidget, QMessageBox, QGridLayout, QPushButton, QLabel, QCalendarWidget
from PyQt5.QtCore import QDate


class DatePickerWidget(QWidget):
    """The class DatePickerWidget give a view of calendar elements"""

    def __init__(self, ref=None):
        """Initialize the widget
        Params;
            ref QWidget object which is calling this one
        """

        super().__init__()
        self.ref = ref

        if self.ref is None:
            self.label_ask = QLabel("When do you want to install this package ? ")
        else:
            package_name = self.ref.name.text()[0].upper() + self.ref.name.text()[1:]
            self.label_ask = QLabel("When do you want to install the <span style=\" "
                                    "font-size:10pt; font-weight:800; color:#000000;\" >%s</span> package ?"
                                    % package_name)
        self.button_now = QPushButton("now")
        self.button_later = QPushButton("later")
        self.button_cancel = QPushButton("cancel")

        self.calendar = QCalendarWidget()
        # Define minimum and maximum dates to launch the installation
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.setMaximumDate(QDate.currentDate().addDays(3))

        self.calendar.resize(300, 200)

        self.layout = QGridLayout()
        self.layout.addWidget(self.label_ask, 0, 0, 1, 3)
        self.layout.addWidget(self.calendar, 1, 0, 1, 3)
        self.layout.addWidget(self.button_now, 2, 0)
        self.layout.addWidget(self.button_now, 2, 0)
        self.layout.addWidget(self.button_later, 2, 1)
        self.layout.addWidget(self.button_cancel, 2, 2)

        self.setLayout(self.layout)

        self.show()

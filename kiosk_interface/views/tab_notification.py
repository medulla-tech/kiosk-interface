#!/usr/bin/python3
# coding: utf-8
"""Declare a notification space for the app"""
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


from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout
from datetime import datetime


class TabNotification(QWidget):

    def __init__(self, app, kiosk):
        super().__init__()
        self.app = app
        self.app.kiosk = kiosk

        self.lay = QVBoxLayout()

        self.text_logs = QTextEdit(self)
        self.text_logs.setReadOnly(True)
        self.text_logs.setEnabled(True)

        self.lay.addWidget(self.text_logs)

        self.setLayout(self.lay)

    def add_notification(self, message):
        date_str = str(datetime.now().year) + "/" + str(datetime.now().month) + "/" + str(str(datetime.now().day)) + \
            " "+ str(datetime.now().hour) + ":" + str(datetime.now().minute)

        msg = "\n"+ date_str + " -- " + message

        logs = self.text_logs.toPlainText()
        logs = logs + "\n"
        logs = logs + msg

        self.text_logs.setText("")
        self.text_logs.setText(logs)

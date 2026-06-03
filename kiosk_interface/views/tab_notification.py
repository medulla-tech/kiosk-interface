#!/usr/bin/python3
# coding: utf-8
"""Declare a notification space for the app"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later


from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout
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
        date_str = (
            str(datetime.now().year)
            + "/"
            + str(datetime.now().month)
            + "/"
            + str(str(datetime.now().day))
            + " "
            + str(datetime.now().hour)
            + ":"
            + str(datetime.now().minute)
        )

        msg = "\n" + date_str + " -- " + message

        logs = self.text_logs.toPlainText()
        logs = logs + "\n"
        logs = logs + msg

        self.text_logs.setText("")
        self.text_logs.setText(logs)

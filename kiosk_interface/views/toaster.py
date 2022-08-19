#!/usr/bin/python3
# coding: utf-8
""" Define a partial view to display packages in the list"""
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


from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, \
    QGridLayout,\
    QPushButton,\
    QLabel,\
    QComboBox

from datetime import datetime

class ToasterWidget(QWidget):
    has_to_send = pyqtSignal(name="has_to_send")

    def __init__(self, app, datas):
        
        super().__init__(None)
        self.app = app

        #
        # Buttons
        #
        self.datas = datas

        self.label_title = None
        self.label_attempts = None

        self.button_now = None
        self.button_later = None

        self.report = None
        self.combo_report = None
        self.combo_value = {"15min":15, "1h":60, "4h":240, "1j":1440}
        
        self.layout = None
        self.timer = None
        self.count_time = 0
        self.toast_response_date = None
        self.init_ui()


    def init_ui(self):
        #self.setVisible(False)
        self.setWindowFlags(Qt.Widget|Qt.CustomizeWindowHint|Qt.WindowTitleHint |Qt.WindowStaysOnTopHint)
        self.label_title = QLabel("Install  %s"%self.datas["name"])
        self.label_attempts = QLabel("You can postpone %s more times"%self.datas["remaining_attempts"])

        self.button_now = QPushButton("Install Now")
        self.button_later = QPushButton("Postpone")

        self.combo_report = QComboBox()
        self.combo_report.addItems(["15min", "1h" ,"4h", "1j"])
        self.layout = QGridLayout()

        self.layout.addWidget(self.label_title, 0, 0, 1, 4)
        self.layout.addWidget(self.label_attempts, 1, 0, 1, 4)

        self.timer = QTimer()
        
        self.timer.start(1000)
        
        button_now_width = 4
        button_now_position = 0
        if "remaining_attempts" in self.datas and self.datas["remaining_attempts"] > 0:
            self.layout.addWidget(self.combo_report, 2, 0, 1, 4)
            self.layout.addWidget(self.button_later, 3, 0, 1, 1)
            button_now_width = 1
            button_now_position = 3
        self.layout.addWidget(self.button_now, 3, button_now_position, 1, button_now_width)

        self.setLayout(self.layout)

        self.button_later.clicked.connect(self.later)
        self.button_now.clicked.connect(self.now)

        
        self.timer.timeout.connect(self.time)

    def show(self):
        super().show()
        if "remaining_attempts" not in self.datas or self.datas["remaining_attempts"] == 0:
            self.now()


    def now(self):
        print("install now")
        self.has_to_send.emit()
        self.timer.stop()
        self.close()

    def later(self):
        print("Send message : install %s in %s min (%s), attempt #%s"%(
            self.datas["uuid"], 
            self.combo_value[self.combo_report.currentText()], 
            self.combo_report.currentText(), 
            self.datas["remaining_attempts"]))
    
        self.has_to_send.emit()
        self.timer.stop()
        self.close()

    def close(self):
        super().close()

    def time(self):
        self.count_time += 1

        print(self.count_time)
#!/usr/bin/python3
# coding: utf-8
"""Declare the Kiosk object"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt6.QtWidgets import (
    QListWidgetItem,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QLineEdit,
    QLabel,
    QTabWidget,
    QGridLayout,
)
from PyQt6.QtGui import QIcon

try:
    from kiosk_interface.views.custom_package_item import CustomPackageWidget
    from kiosk_interface.views.tab_kiosk import TabKiosk
except BaseException:
    from views.custom_package_item import CustomPackageWidget
    from views.tab_kiosk import TabKiosk
import re
import os


class Kiosk(QWidget):
    """This class define the main window of the kiosk"""

    def __init__(self, app):
        """
        Initialize the kiosk object.
        This object set up the mechanism to control the kiosk window
        Params:
            app: QApplication is a reference of the main application
        """
        super().__init__()
        self.app = app
        self.setWindowIcon(QIcon(os.path.join(self.app.datasdir,"kiosk.png")))
        self.setWindowTitle("Medulla Kiosk")

        self.resize(self.app.parameters.width, self.app.parameters.height)

        self.app.logger(
            "info", self.app.translate("Application", "Kiosk main view initialization")
        )
        self.tab_kiosk = TabKiosk(self.app, self)

        self.tabs = QTabWidget(self.app.kiosk)
        self.tabs.addTab(self.tab_kiosk, "Packages")

        grid = QGridLayout(self.app.kiosk)
        grid.addWidget(self.tabs, 1, 1, 1, 1)

        self.setLayout(grid)

    def show(self):
        super().show()

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
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

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
        # --- Medulla header banner: petrol bar holding the brand logo ---
        self.header = QLabel()
        self.header.setObjectName("medullaHeader")
        self.header.setFixedHeight(64)
        self.header.setContentsMargins(18, 0, 0, 0)
        self.header.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        logo = QPixmap(os.path.join(self.app.datasdir, "medulla_logo.png"))
        if not logo.isNull():
            self.header.setPixmap(
                logo.scaledToHeight(44, Qt.TransformationMode.SmoothTransformation)
            )

        self.tab_kiosk = TabKiosk(self.app, self)

        self.tabs = QTabWidget(self.app.kiosk)
        self.tabs.addTab(self.tab_kiosk, "Packages")

        # Body wrapper to give the content some padding under the header
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.addWidget(self.tabs)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.header)
        layout.addWidget(body)

        self.setLayout(layout)

    def show(self):
        super().show()

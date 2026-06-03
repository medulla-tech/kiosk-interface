#!/usr/bin/python3
# coding: utf-8
"""Test the kiosk module"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt6.QtWidgets import QApplication
import sys

try:
    from kiosk_interface.kiosk import Kiosk
except BaseException:
    from kiosk import Kiosk


class TestKiosk:
    app = QApplication(sys.argv)
    kiosk = Kiosk(app)

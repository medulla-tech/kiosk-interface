#!/usr/bin/python3
# coding: utf-8
"""This module launch the kiosk interface"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

class Singleton(object):
    _instances = {}
    def instance(func):
        def wrapper(*args, **kwargs):
            if func not in Singleton._instances:
                Singleton._instances[func] = func(*args, **kwargs)
            return Singleton._instances[func]
        return wrapper

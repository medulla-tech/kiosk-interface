#!/usr/bin/python3
#
# (c) 2016-2022 siveo, http://www.siveo.net
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

from setuptools import setup
from distutils.command.install import INSTALL_SCHEMES

import os
import sys

if sys.platform.startswith("linux"):
    fileconf = os.path.join("/", "etc", "pulse-xmpp-agent")
elif sys.platform.startswith("win"):
    fileconf = os.path.join(os.environ["ProgramFiles"], "Pulse", "etc")
elif sys.platform.startswith("darwin"):
    fileconf = os.path.join("/", "Library", "Application Support", "Pulse", "etc")

for scheme in INSTALL_SCHEMES.values():
    scheme["data"] = os.path.join(scheme["purelib"], "kiosk_interface")

setup(
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords="pulse xmpp kiosk interface",
    name="kiosk_interface",
    version='1.0.0',
    debian_distro="stretch",
    description="XMPP Agent for pulse",
    url="https://www.siveo.net/",
    packages=["kiosk_interface", "kiosk_interface.views"],
    package_data={'': ['__main__.py'], 'kiosk_interface': ['datas/*']},
    test_suite="",
    entry_points={},
    extras_require={},
    install_requires=[
        "PyQt6"],
)

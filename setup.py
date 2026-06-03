# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from distutils.command.install import INSTALL_SCHEMES

import os
import sys

if sys.platform.startswith("linux"):
    fileconf = os.path.join("/", "etc", "pulse-xmpp-agent")
elif sys.platform.startswith("win"):
    fileconf = os.path.join(os.environ["ProgramFiles"], "Medulla", "etc")
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
    keywords="medulla xmpp kiosk interface",
    name="kiosk_interface",
    version='2.0.0',
    debian_distro="stretch",
    description="XMPP Agent for Medulla",
    url="http://www.medulla-tech.io",
    packages=["kiosk_interface", "kiosk_interface.views"],
    package_data={'': ['__main__.py'], 'kiosk_interface': ['datas/*']},
    test_suite="",
    entry_points={},
    extras_require={},
    install_requires=[
        "PyQt6"],
)

#!/usr/bin/env python3
# coding: utf-8
"""Generate Model objects for datas"""
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


class Package(object):
    """Manage the datas for a Package"""

    def __init__(self, row_datas):
        """Initialize a package object
        Args:
            row_datas:  Dict which contains the elements of the package
        """
        if 'name' in row_datas.keys():
            self.name = row_datas['name']
        if 'description' in row_datas.keys():
            self.description = row_datas['description']
        else:
            self.description = ""
        if 'version' in row_datas.keys():
            self.version = row_datas['version']
        else:
            self.version = ""
        if 'actions' in row_datas.keys():
            self.actions = row_datas['actions']
        if 'icon' in row_datas.keys():
            self.icon = row_datas['icon']
        else:
            self.icon = 'kiosk.png'

    def get_all(self):
        return [Package({'name': 'Firefox', 'version': '61.0', 'description': 'Best browser ever',
                  'icon': 'kiosk.png',
                  'actions': ['Install']}),
         Package({'name': 'Thunderbird', 'version': '52.7', 'description': 'If you need to read your mails',
                  'icon': 'kiosk.png',
                  'actions': ['Ask']}),
         Package({'name': 'Vlc', 'icon': 'vlc.png', 'description': 'Video player',
                  'actions': ['Update', 'Launch', 'Delete']}),
         Package({'name': '7zip', 'icon': 'kiosk.png',
                  'actions': ['Launch', 'Delete']})
         ]

    def getname(self):
        return self.name
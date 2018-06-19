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

from server import MessengerToAM
from server import get_datakiosk, set_datakiosk
import os

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
        if 'action' in row_datas.keys():
            self.actions = row_datas['action']
        if 'icon' in row_datas.keys():
            # Test if the icon exists
            if os.path.isfile(os.path.join("datas", row_datas['icon'])):
                self.icon = row_datas['icon']
            else:
                self.icon = 'kiosk.png'
        else:
            self.icon = 'kiosk.png'
        if 'uuid' in row_datas.keys():
            self.uuid = row_datas['uuid']

    def get_all(self):
        """Generage and returns the list of package
        Returns : the list of packages
        """
        datainitialisation = get_datakiosk()
        send_message_to_am('{"action":"kioskLog","type":"info","message":"Generate the package list"}')
        print("___________chang struct______________")
        print(datainitialisation)
        print("_____________________________________")
        list=[]
        for element in datainitialisation:
            list.append(Package(element))
        return list

    def getname(self):
        return self.name


def send_message_to_am(message, ref=None):
    client = MessengerToAM()
    client.send(message.encode('utf-8'))
    get_datakiosk()

    if ref is not None:
        ref.updated.emit()

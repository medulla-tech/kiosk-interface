#!/usr/bin/python3
# coding: utf-8
"""This module launch the kiosk interface"""
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla / Natsu, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
import logging

try:
    # Import for unit tests
    from kiosk_interface.config import ConfParameter
    from kiosk_interface.tray import Tray
    from kiosk_interface.kiosk import Kiosk
    from kiosk_interface.notifier import Notifier
    from kiosk_interface.actions import EventController
    from kiosk_interface.server import MessengerToAM, MessengerFromAM
except BaseException:
    # Import for normal use
    from .config import ConfParameter
    from .tray import Tray
    from .kiosk import Kiosk
    from .notifier import Notifier
    from .actions import EventController
    from .server import MessengerToAM, MessengerFromAM


class Application(QApplication):
    """Generate the main app object"""

    def __init__(self, conf):
        """Initialize the object"""
        super().__init__(sys.argv)  # Initialize the Qapplication
        self.log = logging.getLogger()

        # To add an event :
        # 1 - In Notifier create the signal
        # 2 - In EventController, connect it to the function to call. The function is defined below the
        # EventController constructor.
        # 3 - call my_signal.emit() at the position you want to declare the event
        # 4 - All the application is accessible from anywhere:
        #   self.app is a reference to the main app
        #   self.app.tray is a reference to the Tray
        #   self.app.kiosk is a reference to the Kiosk
        #   self.app.notifier is a reference to the Notifier
        #   self.app.eventCtrl is a reference to the EventController
        #   self.app.parameters is a reference to the Config

        # Shortcuts to some working directories
        self.rootdir = os.path.dirname(__file__)
        self.datasdir = os.path.join(self.rootdir, "datas")
        self.viewsdir = os.path.join(self.rootdir, "views")

        if sys.platform.startswith("win"):
            pidfile = os.path.join("C:\\", "progra~1", "Medulla", "bin", "kiosk.pid")

            import ctypes
            myappid = 'Medulla.kiosk.2.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        else:
            pidfile = os.path.join("/", "tmp", "kiosk.pid")

        with open(pidfile, "w") as pidfb:
            pidfb.write("%s"%os.getpid())
            pidfb.close()

        # Notify the application when something is happening
        self.notifier = Notifier()
        # Action launched when the kiosk emit a notification
        self.eventCtrl = EventController(self)

        self.connected = False
        self.row_message = ""  # Contains the last received message interpreted as dict
        self.message = {}
        self.packages = []  # Contains the packages of the application
        self.last_inventory = ""
        self.temp_inventory = ""

        # Reference to a translate function
        self.translate = QCoreApplication.translate

        # Keep the config parameters in memory
        self.parameters = conf

        # Socket server. It is always running. This module listen and wait the
        # messages from AM
        self.receiver = MessengerFromAM(self)

        self.logger("info", "Initialization")
        self.log.info("Kiosk initialization")
        # The mechanics are launched here
        self.notifier.app_launched.emit()

        self.setWindowIcon(QIcon(os.path.join(self.datasdir, "kiosk.png")))
        self.setApplicationName("Medulla Kiosk")
        # Link the app to its .desktop file so the desktop environment shows the
        # proper name/icon (e.g. GNOME top bar) instead of the interpreter name
        # ("python3"). The name matches /usr/share/applications/medulla-kiosk.desktop.
        self.setDesktopFileName("medulla-kiosk")
        # When the window is closed, the process is not killed
        self.setQuitOnLastWindowClosed(False)

        # Contains the tray app
        self.tray = Tray(self)

        # Contains the kiosk app
        self.kiosk = Kiosk(self)

        # Contains ref to independant windows
        self.independant = {}

        # On desktops without a system tray (e.g. GNOME, which dropped the
        # legacy notification area), the tray icon never shows up, so the user
        # would have no way to open the kiosk. In that case, display the main
        # window directly at startup. Where a tray is available (KDE, Xfce,
        # MATE, Cinnamon...), we keep the discreet tray-driven behaviour.
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.log.info("No system tray available, opening kiosk window directly")
            self.notifier.tray_action_open.emit("")

    def run(self):
        """Launch the main loop"""
        try:
            self.exec()
        except Exception as err:
            self.log.error("Error during execution: %s" % err)

    # Associate a unique sender. This module send messages to AM
    def send(self, message):
        messenger = MessengerToAM(self)
        try:
            messenger.send(message)
        except Exception as err:
            self.log.error("Error during sending %s : %s" % (message, err))

    def logger(self, type, msg):
        """Send log message to Agent Machine.
        Params:
            type: str corresponds to the type of log we want add to the xmpp logs. The types can be :
                - "info"
                - "error"
                - "debug"
            msg: str of the message we want add to log xmpp"""
        message = '{"action": "kioskLog","type": "%s", "message": "%s"}' % (
            type,
            self.translate("Log", msg),
        )
        self.send(message)

    def send_ping(self):
        """Send a ping signal to the AM"""
        signal_presence = '{"action": "presence", "type":"ping"}'
        self.send(signal_presence)

    def send_pong(self):
        """Send a pong signal to the AM"""
        signal_presence = '{"action": "presence", "type":"pong"}'
        self.send(signal_presence)


def notify_running_instance_to_show(conf):
    """Ask an already-running kiosk to bring its window to the foreground.

    Connects to the local socket the running kiosk listens on and sends a
    ``show`` message. Used by the application menu launcher on desktops without
    a system tray (e.g. GNOME). Returns True if a running instance was reached.
    """
    import socket
    import json

    try:
        sock = socket.create_connection(
            (conf.am_server, conf.kiosk_local_port), timeout=2
        )
        sock.sendall(json.dumps({"action": "show"}).encode("utf-8"))
        sock.close()
        return True
    except OSError:
        return False


if __name__ == "__main__":
    conf = ConfParameter()

    # `--show` is used by the desktop menu launcher to reopen the window of an
    # already-running instance. If none is running, fall through and start the
    # kiosk normally.
    if "--show" in sys.argv:
        if notify_running_instance_to_show(conf):
            sys.exit(0)

    format = "%(asctime)s - %(levelname)s -(LAUNCHER)%(message)s"
    formatter = logging.Formatter(format)
    logdir = os.path.dirname(conf.logfilename())
    if os.path.isdir(logdir):
        os.makedirs(logdir, exist_ok=True)
    logging.basicConfig(level=conf.log_level, format=format, filename=conf.logfilename(), filemode="a")

    app = Application(conf)
    app.send_ping()
    app.run()

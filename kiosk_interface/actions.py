import json


class EventController(object):
    """Bind events with actions"""

    def __init__(self, appObject):
        """Manage the connexion between signals and actions
        Param:
            appObject: Application, reference to the main app"""
        self.app = appObject

        self.app.notifier.app_launched.connect(self.action_app_launched)
        self.app.notifier.message_sent_to_am.connect(self.action_message_sent_to_am)
        self.app.notifier.server_cant_send_message_to_am.connect(self.action_server_cant_send_message_to_am)
        self.app.notifier.message_received_from_am.connect(self.action_message_received_from_am)
        self.app.notifier.tray_action_open.connect(self.action_tray_action_open)

    def action_message_received_from_am(self, message=""):
        """Action launched when the kiosk receive a message from Agent Master.
        Param:
            message: str this message is normally a json stringified. In function of the elements contained in the message,
            the action will reacts differently."""

        self.app.message = message
        self.app.logger("info", self.app.translate("Server","Received message %s from AM" % message))

        try:
            decoded = json.loads(self.app.message)

            if "action" in decoded:
                if decoded["action"] == "packages" or decoded["action"] == "update_profile":
                    if "packages_list" in decoded:
                        self.app.packages = decoded["packages_list"]

                elif decoded["action"] == "update_launcher":

                    packages = self.app.packages
                    for package in packages:
                        if package['uuid'] == decoded['uuid']:
                            package['launcher'] = decoded['launcher']
                    self.app.packages = packages

                elif decoded["action"] == "presence":
                    # If the AM send a ping to the kiosk, it answers by a pong
                    if decoded["type"] == "ping":
                        self.app.send_pong()

                    # The AM sendback a pong
                    elif decoded["type"] == "pong":
                        self.app.connected = True

                        print("Connected to the AM")

                self.app.kiosk.search()
        except Exception as error:
            # If the message can't be decoded as json
            print(self.app.translate("Action", "Error when trying to load datas"))
            self.app.logger("error", self.app.translate("Action", "Error when trying to load datas"))

    def action_app_launched(self):
        """Action launched when the kiosk is launched"""
        self.app.logger("info", self.app.translate("Application", "Application launched"))

    def action_message_sent_to_am(self, message):
        """Action launched when a message is sent to the Agent Machine"""
        msg = self.app.translate("Server", "Message sent to AM : ")

        print("info", msg + message)

    def action_server_cant_send_message_to_am(self, message):
        """Action launched when a message is received from the Agent Machine"""
        msg = self.app.translate("Server", "Message can't be sent to AM ")
        print(msg + ": %s" % message)
        self.app.connected = False


    # Launch the kiosk main window
    def action_tray_action_open(self, criterion):
        """Action launched when the open action is pressed in the tray menu"""
        self.app.logger('info', self.app.translate("Kiosk","Initialize the kiosk main window"))

        self.app.kiosk.input_search.setText(criterion)
        self.app.kiosk.search()
        self.app.kiosk.show()

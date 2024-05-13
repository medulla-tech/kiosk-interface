Dev Notes
====

# Communication
The Kiosk communicate (sends and receives) with Agent Machine through TCP socket.

## Configuration

The kiosk read some config files to do its job

### Files

The kiosk read the config files (.ini and .ini.local) located in :

- *C:\Program Files\Pulse\etc\agentconf.ini* for Windows,
- */etc/pulse-xmpp-agent/agentconf.ini* for Linux,
- */Library/Application Support/Pulse/etc/agentconf.ini* for MacOs.

If the config file doesn't exists, a configuration by default is set.

### Default configuration

Here the list of parameters by default

| Section | Option           | Value     | Description                                          |
|:--------|:-----------------|:---------:| ----------------------------------------------------|
| kiosk   | am_local_port    | 8765      | Port for socket listened by Agent Machine           |
| kiosk   | kiosk_local_port | 8766      | Port for socket listened by Kiosk                   |
| kiosk   | am_server        | localhost | Server address where the TCP connections are opened |

To summarize:
- AM -- (TCP/IP : 8766) --> kiosk
- kiosk -- (TCP/IP : 8765) --> AM

Messages sent through the sockets are serialized JSON. 

## List of messages received by the Kiosk

What we see on the kiosk and kiosk behaviours are driven by the messages it receives. In this part we will see the structure of the messages sent by Agent Machine and received by the Kiosk.

All the messages received by the kiosk have an **action** and can have some additionnals parameters.


### Ping

- Desc : The Agent Machine can send a ping to the kiosk to know if it's present or not. This action changes the kiosk status to connected.
- Incomming message :
```json
{
    "action": "presence",
    "type":"ping"
}
```
- response :
```json
{
    "action": "kioskLog",
    "type": "info",
    "message": "Received message from AM"
}
{
    "action": "presence",
    "type":"pong"
}
```

### Package list:

- Desc: Send packages list to the kiosk. It is the main message comming to the kiosk. There is an another message with the action __update_profile__. This message is the same and do the same thing.
- Incomming Message:
    ```json
    {
        "action":"packages", 
        "packages_list":[
            {
                "icon":"firefox.png",
                "name":"firefox",
                "uuid":"aaa",
                "version": "v1",
                "description":"my description",
                "action":["Launch", "Install","Uninstall", "Ask"],
                "launcher" : "QzpcXFByb2dyYW0gRmlsZXNcXE1vemlsbGEgRmlyZWZveFxcZmlyZWZveC5leGU=",
                "status": "Launch",
                "stat": 25
            }
        ]
    }
    ```
- Optionnal keys (on package description):
    - icon: give an icon name to the package. If an icon is found, display it on the kiosk.
    - launcher : the launcher is associated with the Launch button. launcher is a base64 string of the path to the executable.
    - stat: Specify the action advencement. If given, a progress bar will appear below the package in kiosk. It is a float value from 0 to 100 and correspond to a percentage.
     - status: Associate an action button to the stat progress bar.
    If specified, the associated button is disabled unless the stat reach 100 (100%). If a stat is declared in the package, make sure to declare at the end of the package workflow a 100 stat. Like this the package will not be stuck in a transition phase.
    - action: the action key is mandatory, but no can be declared inside.
- Response :
```json
{
    "action": "kioskLog",
    "type": "info",
    "message": "Received message from AM"
}
```
### Progress Notification
- Desc: The Agent Machine can send progression infos. When the stat reach 100, the action button specified in status key is reactivated.
- Incomming message:
```json
{
    "action":"action_kiosknotification",
    "data":{
        "path":"firefox/aaa",
        "stat": 50,
        "status": "Launch"
    }
}
```

### Update launcher
- Desc : Modify a launcher for a specific package in the kiosk
- Incomming message:
```json
{
    "action":"update_launcher",
    "uuid":"aaa",
    "launcher":"L3Vzci9iaW4vZmlyZWZveA=="
}
```


## Messages Sent by the kiosk

### Initialization
- Desc : Ask the package list specific for this kiosk. The package list is depending on the user profiles.
- Message:
```json
{
    "action":"kioskinterface",
    "subaction":"initialization"
}
```
- Resp: a packages or update_profile message

### Log to xmpp
- Desc : Send logs to xmpp agent
- Message :
```json
{
    "action": "kioskLog",
    "type": "info",
    "message": "Initialization"
}
```

### Ask presence
- Desc : Send a presence message to the AM. If the the kiosk is able to send it, the connection is established. Then the kiosk can work normally.
- Message:
```json
{
    "action": "presence",
    "type":"ping"
}
```

### Install package
- Desc : send the installation request to the AM if the Install button is pressed. The difference between the "now install" and "later install" is the datetime sent in this message.
- Message :
```json
{
    "uuid": "aaa",
    "action": "kioskinterfaceInstall",
    "subaction": "Install",
    "utcdatetime": "(2024, 4, 15, 9, 21)"
}
```

### Uninstall package
- Desc : send the uninstall request to the AM if the Uninstall button is pressed.
- Message :
```json
{
    "uuid": "aaa",
    "action": "kioskinterfaceUninstall",
    "subaction": "Uninstall"
}
```

### Ask grants
- Desc : In the defined profile, if the package is associated in the "Ask acknowledgement" list, the user need first to ask the rights to install it.
After this this request need a validation from an administrator.
- Message :
```json
{
    "uuid": "aaa",
    "action": "kioskinterfaceAsk",
    "subaction": "Ask",
    "askuser":"JohnDoe",
    "askdate":"2024-04-15 11:22:10.894378"
}
```
# Project Structure

This representation represents folders by adding / at the end of the name and regular files are normally called. 
We can add some additionnal comments represented by ```The comment```

- kiosk_interface/
    - datas/ ```Assets folder. We can find some icons files```
        - firefox.png 
        - git.png
        - kiosk.png
        - notepad.png
        - thunderbird.png
        - vlc.png
    - views/
        - \_\_init\_\_.py ```Used only to declare views folder as python plugin```
        - custom_package_item.py ```Create a wrapper widget for listbox```
        - custom_search_bar.py ```Create a wrapper widget for searchbar in the tray```
        - date_picked.py ```Create a personnalized datepicker sized for our needs```
        - tab_kiosk.py ```Wrapper for the packages tab, wherein they are displayed.```
        - toaster.py ```Widget where the toaster popup is designed```
    - \_\_init\_\_.py ```Declare the Application class then run it.```
    - actions.py ```All the main actions are declared here```
    - config.py ```The configuration is read by this object```
    - dev_notes.md ```This document```
    - kiosk.py ```Widget where the main window is designed. See also views.tab_kiosk.py```
    - lib.py ```If we need to implement class/function accessible from everywhere```
    - notifier.py ```Static object where all the personnal triggers are declared. These triggers call actions from actions.py```
    - server.py ```TCP sender and receiver```
    - tray.py ```The tray is launched at the kiosk startup```

# Add new behaviours

1. In Notifier create the signal
1. In EventController, connect it to the function to call. The function is defined below the
EventController constructor.
1. call my_signal.emit() at the position you want to declare the event
1. All the application is accessible from anywhere:
```
self.app is a reference to the main app
self.app.tray is a reference to the Tray
self.app.kiosk is a reference to the Kiosk
self.app.notifier is a reference to the Notifier
self.app.eventCtrl is a reference to the EventController
self.app.parameters is a reference to the Config
```

**Note:** 
If You want to create and display a new independant window, make sure you have an attribute in slf.app to store it. If this is not the case, your window will be shown and closed immediately after.

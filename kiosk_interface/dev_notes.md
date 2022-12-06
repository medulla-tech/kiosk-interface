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


Messages sent through the sockets are serialized JSON. 

To summarize :

- send message to localhost:8765 = message to Agent Machine 
- send message to localhost:8766 = message to kiosk



## Messages Received by the Kiosk

What we see on the kiosk and kiosk behaviours are driven by the messages it receives. In this part we will see the structure of the messages sent by Agent Machine and received by the Kiosk.

All the messages received by the kiosk have an **action** and can have some additionnals parameters.

The Agent Machine can send a ping to the kiosk to know if it's present or not.

    {
        "action": "presence",
        "type":"ping"
    }

The Agent Machine can send informative messages to the kiosk :

    {
        "action": "action_kiosknotification",
        "data":{
            "message": "my message"
        }
    }


The Agent Machine can send packages list to the kiosk. Each package can have some parameters :

    # Minimal message
    {
        "action":"packages", 
        "packages_list":[
            {
                "name":"firefox", 
                "uuid":"aaa", 
                "action":[]
            }
        ]
    }

    # Additionnal infos
    {
        "action":"packages", 
        "packages_list":[
            {
                "name":"pkg_name", 
                "uuid":"pkg_uuid", 
                "version" : "V1_0",
                "description": "pkg description",
                "icon":"firefox.png", # This line associate an icon stored in kiosk_dir/datas/
                "action":[]
            }
        ]
    }

    # Add a launcher action
    {
        "action":"packages", 
        "packages_list":[
            {
                "icon":"firefox.png", 
                "name":"firefox", 
                "uuid":"aaa", 
                "action":["Launcher"], # This line add a launcher button
                "launcher" : "C:\\Program Files\\Mozilla Firefox\\firefox.exe" # This line is associated to the Launcher button
            }
        ]
    }

    {
        "action":"packages", 
        "packages_list":[
            {
                "icon":"firefox.png", 
                "name":"firefox", 
                "uuid":"aaa", 
                "version": "v1", 
                "description":"my description",
                "action":["Launch", "Install", "Uninstall", "Ask"],
                "launcher" : "C:\\Program Files\\Mozilla Firefox\\firefox.exe", 
                "status": "Launch", # Correspond to the action name ("Launch", "Install", "Uninstall", "Ask"). Disable the corresponding button
                "stat": 25 # progression (0 to 100%) for the action triggered
                }]}

## Messages Sent by the kiosk

TODO

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
        - tab_notification.py ```Wrapper for the notification tab```
        - toaster.py ```Widget where the toaster popup is designed```
    - \_\_init\_\_.py ```Declare the Application class then run it.```
    - actions.py ```All the main actions are declared here```
    - config.py ```The configuration is read by this object```
    - dev_notes.md ```This document```
    - kiosk.py ```Widget where the main window is designed. See also views.tab_kiosk.py and views.tab_notification.py```
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

# ztp
Cisco Zero Touch Provisioning

This is my zero touch provisioning script.  There are many like it.  But this one is mine.

Short and simple, get'er done script to upgrade the IOS.  There is no logic.  Normally, the script should have some check to make sure it doesn't try to upgrade the IOS a second time.  If the install command is run a second time, the installation will stop with the reason, "Same Image File-No Change".  Currently, the Cisco Catalyst 9300s are shipping with IOS XE 16.12.x installed ( as of December 2021 ).  That version uses Python 2.7.  The script updates IOS XE to 17.3.x, which uses Python 3.6.  The script will error on the first print statement if the upgrade was successfull.

The Python 3.6 script just has the print statements changed.  If you want to use one script that works with both Python 2.7 and Python 3.6, look into the feature "from __future__ import print_function".

To prevent the script from running a second time after a successful upgrade, I changed the prompt to "y" to save the configuration during the installation.  If you have a separate ZTP script or you are using AutoInstall or PNP to configure the switch at a later time, change that prompt back to "n".  You'll probably want to remove "file prompt quiet" and the "UPGRADE" EEM applet when you apply a configuration to the switch.

```
System configuration has been modified.
Press Yes(y) to save the configuration and proceed.
Press No(n) for proceeding without saving the configuration.
Press Quit(q) to exit, you may save configuration and re-enter the command. [y/n/q]
```

It takes about 5 minutes after powering up the switch before the guestshell is started and the script is run.  Total time for the upgrade is about 30 minutes.  Much of this time is because there is a microcode update when upgrading from 16.12.x to 17.3.4.

If you need help figuring out how to change the python in the script, fire up Python in a guestshell.  When testing the script, the switch has to have no startup-config and has to be power cycled.  ZTP will not start after using reload.

```
conf t
  iox
  app-hosting appid guestshell
    vnic management guest-interface 0
    end
!
! Wait for IOX to start
term monitor
!
guestshell enable
!
! Wait for the guestshell to start
!
guestshell run python
```

Note:  In IOS XE 17.3.4, that command will error.  Use "guestshell run python3".

The script will be copied to flash:guest-share/download_script.py.  You can edit the script in the guestshell with vi if needed and run the script.

```
Switch# guestshell
[guestshell@guestshell ~]$ ls -l /flash/guest-share/
total 8
-rw-r--r--. 1 guestshell guestshell 1563 Jan  1 00:01 downloaded_script.py

[guestshell@guestshell ~]$ vi /flash/guest-share/downloaded_script.py

[guestshell@guestshell ~]$ python /flash/guest-share/downloaded_script.py
```

To get more information about the cli module.

```
>>> import cli
>>> help(cli)
Help on package cli:

NAME
    cli

DESCRIPTION
    Copyright (c) 2020 by Cisco Systems, Inc.
    All rights reserved.
    
    Run Cisco IOS CLI commands and receive the output.
    
    This module contains utility functions that run Cisco IOS CLI commands and p
rovide
    the output.

 . . .
 . . .
```


I'm using TFTP.  

```
vlan 100
  name 9300.ztp
int vlan 100
  des 9300.ztp
  ip add 198.51.100.1 255.255.255.0
  no shut
!
ip dhcp exclude-address 198.51.100.1 198.51.100.10
ip dhcp pool 9300_ZTP_Pool
  network 198.51.100.0 255.255.255.0
  default-router 198.51.100.1
  option 150 ip 192.0.2.100
  option 67 ascii 9300_ztp.py
```



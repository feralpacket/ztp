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

Note:  The EEM script is unnecessary if you add "prompt-level none" to the install command.  It appears the command is responding with "y" to any questions as the configuration is saved.  This is a potential problem if you want to run ZTP a second time.  Why would you want to do this?  Well, how do you verify the software upgrade was successful?  One way is to connect a console cable to every switch and run "show version" to verify the IOS version.  Another way is to modify your ZTP script to check the version.  If the IOS version is the target version, have to script do some action to notify something an upgrade is not need ( the upgrade was successful ).  It also depends on how you are going to configure the switch.  Are you going to console in and copy / paste a configuration?  Are you going to use something automated to push a configuration?  And at some point you need to verify the hardware, power supply(ies), fans, and network modules.  Are there any weird, out of the ordinary log messages?

Note:  The DNA Advantage license is needed for the EEM feature.  Also noticed the "prompt-level none" command doesn't always work.  Your mileage may vary.

If you haven't figured this out yet, the result of successfully automating stuff is spending a lot of time looking at the output of the results to verify the automation was successful.  Of course, the verification can also be automated.  Where does that hampster wheel stop?

```
install add file flash:cat9k_iosxe.17.03.05.SPA.bin activate commit prompt-level none
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

Note:  Had a shipment of 9300 switches with 16.12.4 that had to be "kick started" before ZTP would respond.  After configuring iox, running "guestshell enable", and then power cyclying the switch, ZTP worked as expected. 

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
ip dhcp pool 9300_ZTP_POOL
  network 198.51.100.0 255.255.255.0
  default-router 198.51.100.1
  option 150 ip 192.0.2.100
  option 67 ascii 9300_ztp.py
  lease 0 4
```
### SCP

SCP is VRF aware.  If you use SCP instead of TFTP, you'll have to configured the SSH source interface to use the management interface and VRF.
```
ip ssh source-interface gi0/0
```
### DHCP Requests on Vlan 1

Noticed recently, September 2023, Autoinstall / ZTP will send DHCPv4 and DCHPv6 requests out Vlan1.  These were on 9300s shipped with 17.5.1b.  Previously, ZTP only worked with the management interface.  This is important for switches that are normally only connected via fiber.  This means I can start to consider having the hardware team replace switches without having to upgrade the IOS and configure them separately.  Looked through the IOS XE release notes to see when this became a thing.  Couldn't find anything.  Looked through the 9300 and IOS XE documentation.  Again, nothing.  The only thing I did notice was any mention of ZTP only working on the management interface was removed.

### Verification

Even if I start having 9300s configured and updated on site, still have to do some basic checks to verify the switch is working.

```
sh inv
  ! Are the NIMs present?
  ! Are the SFPs present?

sh env all
  ! Are the power supplies and fans present and functioning?

sh logging
  ! Are there any weird log messages that usually are not present with new, out of the box switches?

dir
  ! Are there any crash or dump files?

sh swi
  ! Are all of the switches in the stack present?

sh swi port-stack detail
  ! Are there any errors?
  ! Did the hardware team insert the stack cables properly?
  ! Are the stack cables getting crushed after the cabinet was slammed shut?
  ! Is Cisco having quality control issues, again?

sh logging onboard switch active uptime detail
  ! This command tends to change slightly with switch model and IOS XE version.
    ! sh logging onboard uptime detail
    ! sh logging onboard RP 0 uptime detail
    ! sh logging onboard switch active RP 0 uptime detail
    ! sh logging onboard switch 1 uptime detail
  ! How long has the switch been sitting in inventory?
  ! Did we happen to get an RMA or grey market switch?

```


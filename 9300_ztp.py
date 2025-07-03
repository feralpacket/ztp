import cli
import time

print("\n\n   *** Feralpacket 9300 Zero Touch Provisioning Script ***   \n\n")

print("\n\n   *** Stop prompts and set TFTP blocksize ***   \n\n")
cli.configurep(["file prompt quiet", "end"])
cli.configurep(["ip tftp blocksize 8192", "end"])
time.sleep(10)

print("\n\n   *** Copy image to flash: ***   \n\n")
#cli_command = "copy tftp://192.0.2.1/cat9k_iosxe.17.12.05.SPA.bin flash:cat9k_iosxe.17.12.05.SPA.bin"
# FTP is just so much faster
# Yeap, hard coded credentials
cli_command = "copy ftp://feralpacket:solarwinds123@192.0.2.1/cat9k_iosxe.17.12.05.SPA.bin bootflash:cat9k_iosxe.17.12.05.SPA.bin"
cli.executep(cli_command)
time.sleep(10)

print("\n\n   *** Verify /md5 checksum of image ***   \n\n")
cli_command = "verify /md5 flash:cat9k_iosxe.17.12.05.SPA.bin"
cli.executep(cli_command)
print("\n\n   *** MD5 checksum should be:  e032ebc5e8a9e050635a9b9d97dba49c ***   \n\n")
time.sleep(10)

print("\n\n   *** Configure EEM to install the image ***   \n\n")
eem_commands = ['event manager applet UPGRADE',
                'event none maxrun 600',
                'action 1.0 cli command "enable"',
                'action 2.0 cli command "install add file flash:cat9k_iosxe.17.12.05.SPA.bin activate commit" pattern "y\/n"',
		'action 2.1 cli command "y" pattern "proceed"',
                'action 2.2 cli command "y"'
                ]
cli.configurep(eem_commands)
time.sleep(10)

print("\n\n   *** Write Memory ***   \n\n")
cli_command = "write mem"
cli.excutep(cli_command)
time.sleep(10)

print("\n\n   *** Run EEM to install the image ***   \n\n")
cli_command = "event manager run UPGRADE"
cli.executep(cli_command)
time.sleep(30)

print("\n\n   *** Script complete ***   \n\n")
print("\n\n   *** If you see this, just wait.  It will take a few minutes for the installation to start. ***   \n\n")

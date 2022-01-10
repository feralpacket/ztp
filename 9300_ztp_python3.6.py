import cli
import time

print("\n\n   *** 9300 Zero Touch Provisioning Script - Python 3.6 ***   \n\n")

print("\n\n   *** Stop prompts and set TFTP blocksize ***   \n\n")
cli.configurep(["file prompt quiet", "end"])
cli.configurep(["ip tftp blocksize 8192", "end"])
time.sleep(10)

print("\n\n   *** Copy image to flash: ***   \n\n")
cli_command = "copy tftp://10.201.0.30/cat9k_iosxe.17.03.04.SPA.bin flash:cat9k_iosxe.17.03.04.SPA.bin"
cli.executep(cli_command)
time.sleep(10)

print("\n\n   *** Verify /md5 checksum of image ***   \n\n")
cli_command = "verify /md5 flash:cat9k_iosxe.17.03.04.SPA.bin"
cli.executep(cli_command)
print("\n\n   *** MD5 checksum should be:  4a64084f8108c9645b2ba264048d7665 ***   \n\n")
time.sleep(10)

print("\n\n   *** Configure EEM to install the image ***   \n\n")
eem_commands = ['event manager applet UPGRADE',
                'event none maxrun 600',
                'action 1.0 cli command "enable"',
                'action 2.0 cli command "install add file flash:cat9k_iosxe.17.03.04.SPA.bin activate commit" pattern "y\/n"',
		'action 2.1 cli command "y" pattern "proceed"',
                'action 2.2 cli command "y"'
                ]
cli.configurep(eem_commands)
time.sleep(10)

print("\n\n   *** Run EEM to install the image ***   \n\n")
cli_command = "event manager run UPGRADE"
cli.executep(cli_command)
time.sleep(30)

print("\n\n   *** Script complete ***   \n\n")
print("\n\n   *** If you see this, just wait.  It will take a few minutes for the installation to start. ***   \n\n")

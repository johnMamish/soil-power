#### Connecting to our current Raspberry Pi
"Our" current raspberry pi has Serial: 000000007630b25e. We ought to move to a different solution for managing Raspi ip addresses, but this text doc will do for now. You can get a Raspberry Pi's serial number with `cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`.

 * Make sure that you're connected to GaTech's VPN
 * connect with ssh -Y <your_username>@143.215.189.132. If you don't have an admin account on this Raspi, talk to John.

#### Connecting SBCs to GaTech's network
Assuming that the SBC already has a working Linux flashed to it and you have it connected to a screen and keyboard / mouse, you need to make sure to follow a few steps to connect a new SBC to GaTech's network so that it can be accessed over SSH:

 * Make sure sshd is enabled on startup.
 * Make sure that the device is connected to "gtother" wifi.
 * On another computer, go to https://portal.lawn.gatech.edu/devices and click on the "Register a different device" button.
 * Fill out the form. Make sure to select "disable inbound firewall" under advanced options. If you forget to do this, don't worry, you can change it later.
 * The short-term connection will be granted immediately. The "4-month connection" takes 1 - 2 hours because it needs to be manually reviewed.
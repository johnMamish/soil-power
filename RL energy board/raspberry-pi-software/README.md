### Connecting to our current Raspberry Pi
"Our" current raspberry pi has Serial: 000000007630b25e. We ought to move to a different solution for managing Raspi ip addresses, but this text doc will do for now. You can get a Raspberry Pi's serial number with `cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`.

 * Make sure that you're connected to GaTech's VPN
 * connect with ssh -Y <your_username>@143.215.189.132. The Raspi should have a default lab username and password. If you don't have an admin account on this Raspi, talk to John.

## Raspberry Pi setup
This project nominally uses Raspberry Pi OS on Raspberry Pi 4 model B. To set up a brand new raspberry pi, a few things need to be done:

 1. Use the official Raspberry Pi Imager tool to flash Raspberry Pi OS to an SD card
    
    Make sure to go into the advanced options panel and make the following changes:
      - Select the "Enable SSH" option and choose the "Use password authentication" option
      - Select the "Set username and password" option. Add a default user with the lab username and password. If you're not sure what these are, ask John or Yaman.
      - Select "Configure wireless LAN". Under the options, configure SSID: GTother and Wireless LAN country: US. The password for GTother can be found on [Georgia Tech's LAWN portal](https://portal.lawn.gatech.edu/key) after you sign in under the "GTother PSK" tab.
    
 3. Open the SD card and navigate to the `bootfs` partition.
      - Uncomment the following 2 lines:
        ```
        #dtparam=i2c_arm=on
        #dtparam=spi=on
        ```
      - Add the following line underneath `dtparam=spi=on`
        ```
        enable_uart=1
        ```
  4. Now you can boot up the Rapsberry Pi with the SD card you just made. You can plug it into a monitor and keyboard, or, because of the options we added, you can also access it with a UART adapter. This will let you connect it to LAWN (as described in the next section) without needing a monitor and keyboard.

### Connecting SBCs to GaTech's network
Assuming that the SBC already has a working Linux flashed to it and you have it connected to a screen and keyboard / mouse, you need to make sure to follow a few steps to connect a new SBC to GaTech's network so that it can be accessed over SSH:

 * Make sure sshd is enabled on startup.
 * Make sure that the device is connected to "gtother" wifi.
 * On another computer, go to https://portal.lawn.gatech.edu/devices and click on the "Register a different device" button.
 * Fill out the form. Make sure to select "disable inbound firewall" under advanced options. If you forget to do this, don't worry, you can change it later.
 * The short-term connection will be granted immediately. The "4-month connection" takes 1 - 2 hours because it needs to be manually reviewed.

### Installation requirements
The following Python packages need to be installed with `pip3`:

```
serial, smbus (?), influxdb (?), todo...
```

### Running this code
Just run `./soil_power.py`.

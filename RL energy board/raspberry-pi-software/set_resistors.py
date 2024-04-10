#!/usr/bin/python3

# This utility script sets the electrical load board's pathway: the MFC disconnect switch, potentiometer, and current sense switch.

import RPi.GPIO as GPIO
import smbus2
import spidev
import time
import json
from datetime import datetime

from ad5272 import *
from mcp356x import *
from soilboard import *

import argparse
import json
import numpy as np

parser = argparse.ArgumentParser(description='Sets up MFC load board\'s pathway according to command line arguments.')

parser.add_argument('--current-range', type=str, choices=["low", "high"], default=None,
                    help='what current range should be specified?')
parser.add_argument('--connect-mfc', action='store_true',
                    help='set this flag to connect the mfc')
parser.add_argument('--disconnect-mfc', action='store_true',
                    help='set this flag to disconnect the mfc')
parser.add_argument('--resistance', type=float, default=None,
                    help='Value of load resistor')
parser.add_argument('-q', action='store_true', help='Set this flag to run the command silently')

args = parser.parse_args()

# initialize SPI and devices
sb = SoilBoard()
sb._cleaned_up = True

ad5272_address = 0x2c
i2c = smbus2.SMBus(1)

# setup options
if (args.connect_mfc and args.disconnect_mfc):
    pass
elif (args.connect_mfc):
    sb.connect_mfc()
elif (args.disconnect_mfc):
    sb.disconnect_mfc()

if (args.current_range == "low"):
    sb.select_rsel_lowcurrent()
elif(args.current_range == "high"):
    sb.select_rsel_highcurrent()

if (args.resistance is not None):
    wiper_pos = ad5272_resistance_to_wiper_position(args.resistance)
    set_ad5272_resistor(i2c, 0x2c, wiper_pos)

# Read present settings
current_range = "high" if (GPIO.input(sb.isense_rsel_gpio) == GPIO.LOW) else "low"
mfc_connected = (GPIO.input(sb.isense_rsel_gpio) == GPIO.HIGH)
wiper_pos = ad5272_read_resistor(i2c, 0x2c)

if (not args.q):
    print(f"I_sense shunt current range:  {current_range}")
    print(f"MFC connected?                {mfc_connected}")
    print(f"Load resistor wiper value:  0x{wiper_pos:04x} ({ad5272_wiper_position_to_resistance(wiper_pos): 9.1f}ohm)")
    print()


    

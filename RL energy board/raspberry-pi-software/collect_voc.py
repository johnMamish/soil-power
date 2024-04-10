#!/usr/bin/python3

# This function collects a number of voltage and current readings using the given settings

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

# initialize SPI and devices
sb = SoilBoard()

ad5272_address = 0x2c
i2c = smbus2.SMBus(1)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0

mcp3564_init(spi)

time.sleep(0.03)

# Define the argument parser to read in the inputs
parser = argparse.ArgumentParser(description='Script to log electrical measurements.')
parser.add_argument('logfile', type=str, help='Filename for the output log')
parser.add_argument('--overwrite', action='store_true', help="If set, this will overwrite the log file")
parser.add_argument('--resistance', type=float, default=np.nan,
                    help='Value of shunt resistor, leave as NaN to measure V_oc')
parser.add_argument('--current-range', type=bool, default=False,
                    help='Which current measurement shunt resistor to use. True selects ')
parser.add_argument('--num-meas', type=int, default=100,
                    help='Number of measurements to perform')
parser.add_argument('--actual-voltage', type=float, default=np.nan,
                    help='Ground truth voltage to include in log file')
parser.add_argument('--actual-current', type=float, default=np.nan,
                    help='Ground truth current to include in log file')
parser.add_argument('--disable-adc-calib', action='store_true',
                    help='If this flag is set, measurements are collected without ADC calibration')

# Make sure to log temperature!

args = parser.parse_args()

# disable gaincal and offset if required
if (args.disable_adc_calib):
    # CONFIG3: conversion mode one-shot; default 24-bit ADC format; default CRC settings; OFFSET/GAINCAL enabled
    buf = [mcp3564_make_cmd(CONFIG3, 'w'), (0b10 << 6) | (0b00 << 4) | (0 << 0)]
    spi_xfer_loud(spi, buf)

# Set switches and resistor
wiper_pos = ad5272_resistance_to_wiper_position(args.resistance)
actual_resistance = ad5272_wiper_position_to_resistance(wiper_pos)
if (np.isnan(args.resistance)):
    sb.disconnect_mfc()
else:
    set_ad5272_resistor(i2c, 0x2c, wiper_pos)
    sb.connect_mfc()

sb.select_rsel_highcurrent()

# Take measurements
datas = []

for i in range(args.num_meas):
    time.sleep(0.05)
    data = {}

    # Setup known fields
    if (not np.isnan(args.resistance)): data["resistance (ohms)"] = actual_resistance
    else: data["resistance (ohms)"] = np.nan
    if (not np.isnan(args.actual_voltage)): data["actual_voltage (V)"] = args.actual_voltage
    if (not np.isnan(args.actual_current)): data["actual_current (A)"] = args.actual_current
    data["time (ms)"] = round(time.time() * 1000)
    data["adc calib enabled"] = not args.disable_adc_calib
    
    # Perform a measurement
    v_raw = None
    while (v_raw is None):
        v_raw = mcp3564_read_differential_channel_blocking_raw(spi, 1)
    v_raw_int = (v_raw[0] << 16) | (v_raw[1] << 8) | (v_raw[2] << 0)
    data["voltage (raw)"] = v_raw_int
    data["voltage"] = adc_result_to_voltage(v_raw)

    i_raw = None
    while (i_raw is None):
        i_raw = mcp3564_read_differential_channel_blocking_raw(spi, 0)
    i_raw_int = (i_raw[0] << 16) | (i_raw[1] << 8) | (i_raw[2] << 0)
    data["current_meas (raw)"] = i_raw_int
    
    datas.append(data)

# Write the data to a JSON file
openstr = 'w' if args.overwrite else 'a'
with open(args.logfile, openstr) as json_file:
    for log in datas:
        json.dump(log, json_file, indent=4)


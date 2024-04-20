#!/usr/bin/python3

import os
import time
import csv
import RPi.GPIO as GPIO
import smbus
import spidev
import json
from datetime import datetime

class SoilBoard:
    def __init__(self, voc_switch_gpio=25, isense_rsel_gpio=24):
        self.voc_switch_gpio = voc_switch_gpio
        self.isense_rsel_gpio = isense_rsel_gpio
        self._cleaned_up = False
        self.setup_hw()

    def setup_hw(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.isense_rsel_gpio, GPIO.OUT)
        GPIO.setup(self.voc_switch_gpio, GPIO.OUT)
        self.connect_mfc()
        self.select_rsel_highcurrent()

    def connect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.HIGH)

    def disconnect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.LOW)

    def select_rsel_lowcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.HIGH)

    def select_rsel_highcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.LOW)

    def cleanup(self):
        if not self._cleaned_up:
            GPIO.cleanup()
            self._cleaned_up = True

    def __del__(self):
        self.cleanup()

def set_ad5272_resistor(i2c, addr, wiper_position):
    i2c.write_i2c_block_data(addr, 0x1c, [0x02])  # Unlock the resistor
    command = [(1 << 2) | ((wiper_position >> 8) & 0x03), (wiper_position & 0xff)]
    i2c.write_i2c_block_data(addr, command[0], command[1:])

def mcp3564_init(spi):
    spi.xfer([1, (0b10 << 4) | (0b10 << 0)])  # CONFIG0: use internal oscillator, no current bias
    spi.xfer([2, (0b01 << 6) | (0b0101 << 2)])  # CONFIG1: oversample = 1024

def mcp3564_read_differential_channel_blocking(spi, channel_no):
    # Setup MUX
    chan_p = (2 * channel_no) & 0x0f
    chan_n = (chan_p + 1) & 0x0f
    spi.xfer([(1 << 6) | (chan_p << 4) | (chan_n << 0)])  # Start reading
    # Wait for the conversion to complete
    while True:
        if (spi.xfer([5, 0])[1] & (1 << 6)) == 0:
            break
        time.sleep(0.001)
    adc_data = spi.xfer([0, 0, 0, 0])
    return (adc_data[1] << 16) | (adc_data[2] << 8) | adc_data[3]

# Define resistance values and measurement interval
resistances = [100000, 50000, 25000, 12500, 6200, 3100, 1500]  # Ohms
measurement_interval = 500  # seconds

def log_measurements(spi, i2c, ad5272_address, resistor_value, file_path):
    with open(file_path, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        set_ad5272_resistor(i2c, ad5272_address, resistor_value)
        start_time = time.time()
        while (time.time() - start_time) < measurement_interval:
            i_reading = mcp3564_read_differential_channel_blocking(spi, 0)
            v = mcp3564_read_differential_channel_blocking(spi, 1)
            i = i_reading / (4.7 * 200)  # Adjust this calculation as needed for calibration
            power = v * i
            log_entry = [
                f"{time.time() - start_time:2.1f}",
                f"{1000*i:2.3f}",
                f"{v:1.5f}",
                f"{power*1000:2.3f}",
                f"{resistor_value:5.0f}"
            ]
            csv_writer.writerow(log_entry)
            time.sleep(1)

# Main execution
file_path = "measurement_log.csv"
if not os.path.exists(file_path):
    with open(file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Time (s)", "Current (mA)", "Voltage (V)", "Power (mW)", "Resistance (Ohms)"])

try:
    sb = SoilBoard()
    i2c = smbus.SMBus(1)
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 100000
    spi.mode = 0

    mcp3564_init(spi)
    for resistance in resistances:
        sb.disconnect_mfc()
        log_measurements(spi, i2c, 0x2c, 1023, file_path)  # Simulate open circuit
        sb.connect_mfc()
        log_measurements(spi, i2c, 0x2c, resistance, file_path)
finally:
    sb.cleanup()
    spi.close()
    i2c.close()
    print("Measurement sequence completed.")

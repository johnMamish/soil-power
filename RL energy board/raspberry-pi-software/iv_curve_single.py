#!/usr/bin/python3

import RPi.GPIO as GPIO
import smbus
import spidev
import time
import json
from datetime import datetime

from ad5272 import *
from mcp356x import *
from soilboard import *

# initialize SPI and devices
sb = SoilBoard()

ad5272_address = 0x2c
i2c = smbus.SMBus(1)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0

mcp3564_init(spi)

sb.disconnect_mfc()
time.sleep(0.03)

# sanity check - just read differential channel 1 over and over
while (True):
    sb.disconnect_mfc()
    time.sleep(0.1)
    v = mcp3564_read_differential_channel_blocking(spi, 1)
    print(f"open circuit voltage = {v:1.5f}")

    #sb.connect_mfc()
    #time.sleep(0.1)
    #v = mcp3564_read_differential_channel_blocking(spi, 1)
    #print(f"closed circuit voltage = {v:1.5f}")



calibration_data = {
	'voltage_scale': 1.0,
	'voltage_offset': 0.0,
	'current_scale': 1.0,
	'current_offset': 0.0
}

def apply_calibration(raw_value, scale, offset):
	return (raw_value * scale) + offset

def log_to_json(data, file_path='validation_log.json'):
	try:
		with open(file_path, 'w') as file:
			json.dump(data, file, indent = 4)
	except Exception as e:
		print(f"Error logging data to {file_path}: {e}")

def perform_measurements_and_log():
	log_data = {'measurements': [], 'timestamp': datetime.now().isoformat()}
	max_resistance_info = {'max_resistance': 0, 'potentiometer_setting': 0, 'channel': None}

	try:
		sb.connect_mfc()

		for i in range(0, 300, 5):
			set_ad5272_resistor(i2c, ad5272_address, i)
			time.sleep(0.01)

			for channel in range(3):
				i_reading = mcp3564_read_differential_channel_blocking(spi, 0)
				v = mcp3564_read_differential_channel_blocking(spi, 1)

				calibrated_current = apply_calibration(i_reading / (4.7 * 200), \
									   calibration_data['current_scale'], \
									   calibration_data['current_offset'])

				calibrated_voltage = apply_calibration(v, \
									   calibration_data['voltage_scale'], \
									   calibration_data['voltage_offset'])

				if calibrated_current > 0:
					resistance = calibrated_voltage / calibrated_current
					power = calibrated_voltage * calibrated_current

					measurement = {
						'channel': channel,
						'potentiometer_setting': i,
						'current_mA'	  : 1000 * calibrated_current,
						'voltage_V'		  : calibrated_voltage,
						'power_mW'		  : 1000 * power,
						'resistance_ohms' : resistance
					}

					log_data['measurements'].append(measurement)
					print(f"current = {measurement['current_mA']: 2.3f}mA, \
							voltage = {measurement['voltage_V']: 1.5f}V, \
							power = {measurement['power_mW']: 2.3f}mW, \
							resistance = {measurement['resistance_ohms']: 5.0f}mA")

					if resistance > max_resistance_info['max_resistance']:
						max_resistance_info.update({
							'max_resistance': resistance,
							'channel': channel,
							'potentiometer_setting': i,
							'power_mW': power * 1000
						})


			# ~ resistor = (i / 1024) * 50000
			# ~ set_ad5272_resistor(i2c, ad5272_address, i * 3)
			# ~ time.sleep(0.01)
			# ~ i_reading = mcp3564_read_differential_channel_blocking(spi, 0)
			# ~ v = mcp3564_read_differential_channel_blocking(spi, 1)

			# ~ calibrated_current = apply_calibration(i_reading / (4.7 * 200), \
									   # ~ calibration_data['current_scale'], \
									   # ~ calibration_data['current_offset'])

			# ~ calibrated_voltage = apply_calibration(v, \
									   # ~ calibration_data['voltage_scale'], \
									   # ~ calibration_data['voltage_offset'])

			# ~ power = calibrated_current * calibrated_voltage

			# ~ measurement = {
				# ~ 'current_mA'	  : 1000 * calibrated_current,
				# ~ 'voltage_V'		  : calibrated_voltage,
				# ~ 'power_mW'		  : 1000 * power,
				# ~ 'resistance_ohms' : resistor
			# ~ }

			# ~ log_data['measurements'].append(measurement)
			# ~ print(f"current = {measurement['current_mA']: 2.3f}mA, \
					# ~ voltage = {measurement['voltage_V']: 1.5f}V, \
					# ~ power = {measurement['power_mW']: 2.3f}mW, \
					# ~ resistance = {resistor: 5.0f}mA")


	except KeyboardInterrupt:
		print("\n Process interrupted by user. Savig log data...")
	finally:
		log_to_json(log_data)
		print('Max resistance info: ', max_resistance_info)
		print("Log data saved!")


#perform_measurements_and_log()

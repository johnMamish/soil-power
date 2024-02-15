#!/usr/bin/python3

import RPi.GPIO as GPIO
import smbus
import spidev
import time
import json
from datetime import datetime

class SoilBoard:
    def __init__(self, voc_switch_gpio=25, isense_rsel_gpio=24):
        self.voc_switch_gpio = voc_switch_gpio
        self.isense_rsel_gpio = isense_rsel_gpio

        self._cleaned_up = False
        
        self.setup_hw()
        
    def setup_hw(self):
        # gpios
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.isense_rsel_gpio, GPIO.OUT)
        GPIO.setup(self.voc_switch_gpio, GPIO.OUT)
        self.connect_mfc()
        self.select_rsel_highcurrent()
        
        # i2c
        #self.ad5272_address = 0x2c
        #self.i2c = smbus.SMBus(1)

        # SPI
        #self.spi = spidev.SpiDev()

    def connect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.HIGH)
        
    def disconnect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.LOW)

    def select_rsel_lowcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.HIGH)
        
    def select_rsel_highcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.LOW)
        
    def cleanup(self):
        if (not self._cleaned_up):
            GPIO.cleanup()
            self._cleaned_up = True
        
    def __del__(self):
        self.cleanup()
        

def set_ad5272_resistor(i2c, addr, wiper_position):
    # unlock the resistor
    i2c.write_i2c_block_data(addr, 0x1c, [0x02])
    
    command_number = 1
    command_data = wiper_position
    command = ([(command_number << 2) | ((command_data >> 8) & 0x03), \
                (command_data & 0xff)])
    #print(f"setting ad5272 resistor: cmd = {command}")
    
    i2c_result = i2c.write_i2c_block_data(addr, command[0], command[1:])

ADCDATA = 0x00
CONFIG0 = 0x01
CONFIG1 = 0x02
CONFIG2 = 0x03
CONFIG3 = 0x04
IRQ     = 0x05
MUX     = 0x06
SCAN    = 0x07
TIMER   = 0x08
OFFSETCAL = 0x09
GAINCAL = 0x0a
LOCK    = 0x0d
CRCCFG  = 0x0f

def mcp3564_make_cmd(addr, rw):
    CHIP_ADDR = 1
    if (rw == 'r'):
        rw = 3
    elif (rw == 'w'):
        rw = 2
    else:
        rw = 1
    return ((CHIP_ADDR << 6) | (addr & 0x0f) << 2) | rw

def array_to_hex(buf):
    return ''.join([f'{x:02x} ' for x in buf])

def spi_xfer_loud(spi, buf):
    print(f"SPI transmitting: {''.join([f'{x:02x} ' for x in buf])}")
    spi.xfer(buf)
    print(f"SPI recieved:     {''.join([f'{x:02x} ' for x in buf])}")
    print()
    
def mcp3564_init(spi):
    # CONFIG0: use internal oscillator, no current bias, turn on ADC in standby
    buf = [mcp3564_make_cmd(CONFIG0, 'w'), (0b10 << 4) | (0b10 << 0)]
    spi_xfer_loud(spi, buf)

    # CONFIG1: AMCLK = MCLK/2; oversample = 1024 (final data rate of 600Hz)
    buf = [mcp3564_make_cmd(CONFIG1, 'w'), (0b01 << 6) | (0b0101 << 2)]
    spi_xfer_loud(spi, buf)    

    # CONFIG2: don't do anything; fine with default settings.

    # CONFIG3: conversion mode one-shot; default 24-bit ADC format; default CRC settings; OFFSET/GAINCAL disabled
    buf = [mcp3564_make_cmd(CONFIG3, 'w'), (0b10 << 6) | (0b00 << 4) | 0]
    spi_xfer_loud(spi, buf)

    # Enable IRQ pin; note a quirk with this chip: either the IRQ output must be enabled or the IRQ pin must be
    # pulled up for ADC conversions to work
    buf = [mcp3564_make_cmd(IRQ, 'w'), (0b01 << 2) | (1 << 1) | (1 << 0)]
    spi_xfer_loud(spi, buf)
    
    # read IRQ register
    buf = [mcp3564_make_cmd(IRQ, 'r'), 0]
    spi_xfer_loud(spi, buf)

def adc_result_to_voltage(buf, gain=1.0):
    VREF = 3.32
    i = (buf[0] << 16) | (buf[1] << 8) | (buf[2] << 0)
    return VREF * (i / 8388608) / gain
    
def mcp3564_read_differential_channel_blocking(spi, channel_no):
    # setup mux
    chan_p = (2 * channel_no) & 0x0f
    chan_n = (chan_p + 1) & 0x0f
    buf = [mcp3564_make_cmd(MUX, 'w'), ((chan_p << 4) | (chan_n << 0))]
    spi.xfer(buf)
    
    # start reading with 'fast command'
    buf = [(1 << 6) | (0b1010 << 2)]
    spi.xfer(buf)

    # poll conversion done flag
    while (True):
        buf = [mcp3564_make_cmd(IRQ, 'r'), 0]
        spi.xfer(buf)
        if (not(buf[1] & (1 << 6))):
            break
        time.sleep(0.001)
                
    buf = [mcp3564_make_cmd(ADCDATA, 'r'), 0, 0, 0]
    spi.xfer(buf)
    return adc_result_to_voltage(buf[1:])

# initialize SPI and devices
sb = SoilBoard()

ad5272_address = 0x2c
i2c = smbus.SMBus(1)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000
spi.mode = 0

mcp3564_init(spi)

sb.disconnect_mfc()
time.sleep(0.03)
v = mcp3564_read_differential_channel_blocking(spi, 1)
print(f"open circuit voltage = {v:1.5f}")

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


perform_measurements_and_log()

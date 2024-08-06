import RPi.GPIO as GPIO
import smbus
import spidev
import time

from ad5272 import *
from mcp356x import *

class SoilBoard:
    def __init__(self, i2c_bus=1, voc_switch_gpio=25, isense_rsel_gpio=24):
        self.voc_switch_gpio = voc_switch_gpio
        self.isense_rsel_gpio = isense_rsel_gpio

        self.i2c_bus = i2c_bus

        self._cleaned_up = False

        self.setup_hw()

    def setup_hw(self):
        """
        Configures all GPIOs and hardware interfaces.
        Also does any necessary initialization on the external chips.
        """

        # gpios
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.isense_rsel_gpio, GPIO.OUT)
        GPIO.setup(self.voc_switch_gpio, GPIO.OUT)
        self.connect_mfc()
        self.select_rsel_highcurrent()

        # i2c
        self.ad5272_address = 0x2c
        self.i2c = smbus.SMBus(self.i2c_bus)

        # SPI
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = 1000000
        spi.mode = 0
        mcp3564_init(spi)

    def connect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.HIGH)

    def disconnect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.LOW)

    def select_rsel_lowcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.HIGH)

    def select_rsel_highcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.LOW)

    def set_resistor_value(self, resistance):
        """
        Sets the resistance on the soilboard to the closest available wiper value to the
        requested value in ohms.
        Returns the difference between the set resistance and the actual resistance.
        """
        wiper_pos = ad5272_resistance_to_wiper_position(resistance);
        set_ad5272_resistor(self.i2c, self.ad5272_address, wiper_pos)
        return ad5272_wiper_position_to_resistance(wiper_pos) - resistance

    def get_resistor_value(self):
        """
        returns the current resistor value in ohms
        """
        return ad5272_wiper_position_to_resistance

    def read_voltage(self):
        """
        """

    def read_adc_temperature(self):
        """
        """

    def cleanup(self):
        if (not self._cleaned_up):
            GPIO.cleanup()
            self._cleaned_up = True

    def __del__(self):
        self.cleanup()

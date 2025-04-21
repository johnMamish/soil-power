from logger_types import Sensor
import tempfile
import time
import numpy as np

import spidev
import smbus2
from mcp356x import *
from ad5272 import *

from adc_cs import ADCNum, chip_select as adc_chip_select

class PCB(Sensor):
    def __init__(self, name):
        super().__init__(name)
        self.spi = spidev.SpiDev()

        self.ad5272_address = 0x2c
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000
        self.spi.mode = 0
        
        mcp3564_init(self.spi)

        time.sleep(0.03)
        
        buf = [mcp3564_make_cmd(CONFIG3, 'w'), (0b10 <<6) | (0b00 <<4) | (0 <<0)]
        spi_xfer_loud(self.spi, buf)

        self.wiper_pos = ad5272_resistance_to_wiper_position(np.nan)
        actual_resistance = ad5272_wiper_position_to_resistance(np.nan)


    def read_adc(self, poll_time, adcNum = ADCNum.ADC0):
        adc_chip_select(adcNum)
        resistance = str(np.nan)
        v_raw = None
        while v_raw is None:
            v_raw = mcp3564_read_differential_channel_blocking_raw(self.spi, 1)
        v_raw_int = (v_raw[0] << 16) | (v_raw[1] << 8) | (v_raw[2] << 0)
        v = adc_result_to_voltage(v_raw, VREF=5.3)

        i_raw = None
        while i_raw is None:
            i_raw = mcp3564_read_differential_channel_blocking_raw(self.spi, 0)
        i_raw_int = (i_raw[0] << 16) | (i_raw[1] << 8) | (i_raw[2] << 0)

        r_time = round(time.time() * 1000)
        return dict(
            name=self.name,
            data = dict(
                voltage_raw=v_raw_int,
                current_raw=i_raw_int,
                time=r_time,
                voltage=v,
                resistance=resistance,
                poll_time=poll_time
            )
        )

    def read(self, poll_time):
        return {
            str(ADCNum.ADC0): self.read_adc(poll_time, ADCNum.ADC0),
            str(ADCNum.ADC1): self.read_adc(poll_time, ADCNum.ADC1),
        }




if __name__ == "__main__":
    sensor = PCB("1")
    while True:
        print(sensor.read(time.time()))
        time.sleep(0.05)

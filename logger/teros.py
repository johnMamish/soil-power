from logger_types import Sensor
import serial
import time
from util import get_curr_serial_device


class TerosArduino(Sensor):
    def __init__(self, name):
        super().__init__(name)
        self._serial_port = ""
        self._serial_init = False
        self.serial_verify()

    def serial_verify(self):
        try:
            self.serial_connect()
        except:
            self._serial_init = False
            return
        if not self._serial_init:
            self.serial = serial.Serial(self._serial_port, 9600, timeout=1)
            time.sleep(2)
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            bytes_w = self.serial.write(b"S\n")
            response = self.serial.readline().decode('utf-8').strip()
            if response != "U":
                raise Exception("Unable to connect to Arduino")
        self._serial_init = True


    def serial_connect(self):
        serial_port = get_curr_serial_device()
        if self._serial_port != None and self._serial_port == serial_port:
            return
        self._serial_init = False
        self._serial_port = serial_port

    def read(self, poll_time):
        self.serial_verify()
        if self._serial_init == False:
            return dict(name=self.name, data=dict(poll_time=poll_time, msg="not connected via serial"))
        self.serial.write(b"R\n")
        response = self.serial.readline().decode('utf-8').strip()
        if len(response) <= 0:
            return dict(
                name = self.name,
                data = dict(poll_time = poll_time)
            )
        response=response.split(",")
        return dict(
            name = self.name,
            data = dict(
                temperature=float(response[2]),
                volumetric_water_content=float(response[1]),
                electric_conductivity=float(response[3]),
                elapsed_time=int(response[0]),
                poll_time=poll_time,
                msg="connected via serial"
            )
        )


if __name__ == '__main__':
    sensor = TerosArduino("1")
    while True:
        print(sensor.read(time.time()))
        time.sleep(0.05)
        

from logger_types import Sensor
import serial
import time


class TerosArduino(Sensor):
    def __init__(self, name):
        super().__init__(name)
        self.serial = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
        time.sleep(2)
        #self.serial = serial.Serial()
        #self.serial.port = "/dev/ttyACM0"
        #self.serial.baudrate = "9600"
        #self.serial.timeout = 1
        #self.serial.setDTR(True)
        #self.serial.open()
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        bytes_w = self.serial.write(b"S\n")
        response = self.serial.readline().decode('utf-8').strip()
        if response != "U":
            raise Exception("Unable to connect to Arduino")

    def read(self, poll_time):
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
                poll_time=poll_time
            )
        )


if __name__ == '__main__':
    sensor = TerosArduino("1")
    while True:
        print(sensor.read(time.time()))
        time.sleep(0.05)
        

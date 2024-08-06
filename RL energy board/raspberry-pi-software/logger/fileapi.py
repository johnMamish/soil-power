from logger_types import SensorAdapter
import time
from json import dumps

class FilePusher(SensorAdapter):
    def __init__(self, name, sensor, file):
        super().__init__(name, sensor)
        self.filename = file

    def push_data(self):
        with open(self.filename, "a") as f:
            f.write(dumps(self.sensor.read(time.time())) + "\n")

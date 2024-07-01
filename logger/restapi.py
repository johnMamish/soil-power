from logger_types import SensorAdapter
from requests import post
import time

class RESTPusher(SensorAdapter):
    def __init__(self, name, sensor, url, endpoint):
        super().__init__(name, sensor)
        self.endpoint = endpoint
        self.url = url
    def push_data(self):
        post(f"{self.url}/{self.endpoint}", json=dict(
            name=self.name,
            data=self.sensor.read(time.time())
        ))

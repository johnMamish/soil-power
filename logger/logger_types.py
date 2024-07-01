class Sensor:
    def __init__(self, name):
        self.name = name
    def read(self, poll_time): # should return the data being read in appropriate format
        raise NotImplementedError()

class SensorAdapter:
    def __init__(self, name, sensor):
        self.name = name
        self.sensor = sensor
    def push_data(self):
        raise NotImplementedError()

class PipelineIntervalSensor:
    def __init__(self, name, interval, adapter):
        self.name = name
        self.interval = interval
        self.adapter = adapter

    def register(self):
        from threading import Event, Thread
        self.event = Event()
        def loop():
            while not self.event.wait(self.interval):
                try:
                    self.adapter.push_data()
                except Exception as e:
                    print(e)
        Thread(target=loop).start()

from teros import TerosArduino
from pcb import PCB
from restapi import RESTPusher as adapter
from fileapi import FilePusher as fadapter

from logger_types import PipelineIntervalSensor as PIS

TASKS = [
        #PIS("PCB", 1, adapter("PCB Pusher", PCB("PCB 1"), "http://localhost", "/recv")),
        #PIS("Teros", 1, adapter("Teros Pusher", TerosArduino("Teros Group 1"), "http://localhost", "/recv"))
        PIS("Teros", 60, fadapter("Teros File", TerosArduino("Teros Group 1"), "data/exp1.log"))
]

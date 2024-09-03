import subprocess
import re

def get_curr_serial_device():
    ret = re.findall(r"ttyACM(\d+)", subprocess.check_output("ls /dev", shell=True).decode('utf-8'))
    if len(ret) != 1:
        raise Exception(f"There are {'no' if len(ret) == 0 else 'multiple'} serial devices connected to this device")
    return f'/dev/ttyACM{ret[0]}'

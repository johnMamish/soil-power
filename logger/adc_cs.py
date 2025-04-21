Python 3.12.1 (v3.12.1:2305ca5144, Dec  7 2023, 17:23:38) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> 
... import RPi.GPIO as GPIO
... import time
... 
... from enum import Enum
... 
... class ADCNum(Enum):
...     ADC0=0
...     ADC1=1
... 
... CS1_PIN = 7  # ADC1
... CS2_PIN = 8  # ADC0
... 
... # Setup
... GPIO.setmode(GPIO.BCM)
... GPIO.setup(CS1_PIN, GPIO.OUT)
... GPIO.setup(CS2_PIN, GPIO.OUT)
... 
... # Both Chips start de-selected
... GPIO.output(CS1_PIN, GPIO.HIGH)
... GPIO.output(CS2_PIN, GPIO.HIGH)
... 
... 
... def chip_select(ADC_select):   #ADC"0" or ADC"1"
...     if ADC_select == ADCNum.ADC1:
...         GPIO.output(CS2_PIN, GPIO.HIGH)
...         GPIO.output(CS1_PIN, GPIO.LOW)
...     elif ADC_select == ADCNum.ADC0:
...         GPIO.output(CS1_PIN, GPIO.HIGH)
...         GPIO.output(CS2_PIN, GPIO.LOW)
...     else:
...         raise ValueError("Invalid selection: must be ADC0 or ADC1")

class SoilBoard:
    def __init__(self, voc_switch_gpio=25, isense_rsel_gpio=24):
        self.voc_switch_gpio = voc_switch_gpio
        self.isense_rsel_gpio = isense_rsel_gpio

        self._cleaned_up = False

        self.setup_hw()

    def setup_hw(self):
        # gpios
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.isense_rsel_gpio, GPIO.OUT)
        GPIO.setup(self.voc_switch_gpio, GPIO.OUT)
        self.connect_mfc()
        self.select_rsel_highcurrent()

        # i2c
        #self.ad5272_address = 0x2c
        #self.i2c = smbus.SMBus(1)

        # SPI
        #self.spi = spidev.SpiDev()

    def connect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.HIGH)

    def disconnect_mfc(self):
        GPIO.output(self.voc_switch_gpio, GPIO.LOW)

    def select_rsel_lowcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.HIGH)

    def select_rsel_highcurrent(self):
        GPIO.output(self.isense_rsel_gpio, GPIO.LOW)

    def cleanup(self):
        if (not self._cleaned_up):
            GPIO.cleanup()
            self._cleaned_up = True

    def __del__(self):
        self.cleanup()

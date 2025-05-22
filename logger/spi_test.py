import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 500000
spi.mode = 0

CMD_RESET = 0x01
CMD_READ_ADC = 0x43

def test_mcp3564():
    try:
        spi.xfer2([CMD_RESET])
        time.sleep(0.1)
        response = spi.xfer2([CMD_READ_ADC, 0x00, 0x00, 0x00])
        print("Response from MCP3564:", response)
        
        if any(response):
            print("MCP3564 appears to be responding!")
        else:
            print("No data received. Check connections and configuration.")
            
    except Exception as e:
        print("Error communicating with MCP3564:", e)
    finally:
        spi.close()

print("Testing MCP3564 connection...")
test_mcp3564()


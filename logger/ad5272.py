import smbus2

def set_ad5272_resistor(i2c, addr, wiper_position):
    # unlock the resistor
    i2c.write_i2c_block_data(addr, 0x1c, [0x02])

    command_number = 1
    command_data = wiper_position
    command = ([(command_number << 2) | ((command_data >> 8) & 0x03), \
                (command_data & 0xff)])
    #print(f"setting ad5272 resistor: cmd = {command}")

    i2c_result = i2c.write_i2c_block_data(addr, command[0], command[1:])

def ad5272_wiper_position_to_resistance(wip):
    """
    This utility function takes in an int on [0, 1024) and returns a float corresponding to 
    the reistance value for that wiper position
    """
    return (wip / 1023.) * 100000.

def ad5272_resistance_to_wiper_position(r):
    """
    This utility function returns the wiper position that's closest to the given resistance.
    """
    # Coerce resistance into range [0, 100,000]
    r = max(0., min(r, 100000.))
    wip = int(round(1023 * (r / 100000.)))
    return wip
    
def ad5272_read_resistor(i2c, addr):
    """
    Reads the current wiper position of the resistor returning an int in [0, 1023]
    Note that we have the ad5272-xxxx-100. This means that we have 1024 taps across 100kohm.
    A tap value of 0x000 should give 0 ohms; a tap value of 0x3ff should give 100kohm.
    """
    wr_msg = smbus2.i2c_msg.write(addr, [(0b0010 << 2) | (0), 0])
    rd_msg = smbus2.i2c_msg.read(addr, 2)
    i2c.i2c_rdwr(wr_msg)
    i2c.i2c_rdwr(rd_msg)
    
    data = list(rd_msg)
    return (int(data[0]) << 8) | (int(data[1]))

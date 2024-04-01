def set_ad5272_resistor(i2c, addr, wiper_position):
    # unlock the resistor
    i2c.write_i2c_block_data(addr, 0x1c, [0x02])

    command_number = 1
    command_data = wiper_position
    command = ([(command_number << 2) | ((command_data >> 8) & 0x03), \
                (command_data & 0xff)])
    #print(f"setting ad5272 resistor: cmd = {command}")

    i2c_result = i2c.write_i2c_block_data(addr, command[0], command[1:])

#!/usr/bin/python3


ADCDATA = 0x00
CONFIG0 = 0x01
CONFIG1 = 0x02
CONFIG2 = 0x03
CONFIG3 = 0x04
IRQ     = 0x05
MUX     = 0x06
SCAN    = 0x07
TIMER   = 0x08
OFFSETCAL = 0x09
GAINCAL = 0x0a
LOCK    = 0x0d
CRCCFG  = 0x0f

def mcp3564_make_cmd(addr, rw):
    CHIP_ADDR = 1
    if (rw == 'r'):
        rw = 3
    elif (rw == 'w'):
        rw = 2
    else:
        rw = 1
    return ((CHIP_ADDR << 6) | (addr & 0x0f) << 2) | rw

def array_to_hex(buf):
    return ''.join([f'{x:02x} ' for x in buf])

def spi_xfer_loud(spi, buf):
    print(f"SPI transmitting: {''.join([f'{x:02x} ' for x in buf])}")
    spi.xfer(buf)
    print(f"SPI recieved:     {''.join([f'{x:02x} ' for x in buf])}")
    print()

def mcp3564_init(spi):
    # CONFIG0: use internal oscillator, no current bias, turn on ADC in standby
    buf = [mcp3564_make_cmd(CONFIG0, 'w'), (0b10 << 4) | (0b10 << 0)]
    spi_xfer_loud(spi, buf)

    # CONFIG1: AMCLK = MCLK/2; oversample = 1024 (final data rate of 600Hz)
    buf = [mcp3564_make_cmd(CONFIG1, 'w'), (0b01 << 6) | (0b0101 << 2)]
    spi_xfer_loud(spi, buf)

    # CONFIG2: don't do anything; fine with default settings.

    # CONFIG3: conversion mode one-shot; default 24-bit ADC format; default CRC settings; OFFSET/GAINCAL disabled
    buf = [mcp3564_make_cmd(CONFIG3, 'w'), (0b10 << 6) | (0b00 << 4) | 0]
    spi_xfer_loud(spi, buf)

    # Enable IRQ pin; note a quirk with this chip: either the IRQ output must be enabled or the IRQ pin must be
    # pulled up for ADC conversions to work
    buf = [mcp3564_make_cmd(IRQ, 'w'), (0b01 << 2) | (1 << 1) | (1 << 0)]
    spi_xfer_loud(spi, buf)

    # read IRQ register
    buf = [mcp3564_make_cmd(IRQ, 'r'), 0]
    spi_xfer_loud(spi, buf)

def adc_result_to_voltage(buf, gain=1.0):
    VREF = 3.32
    i = (buf[0] << 16) | (buf[1] << 8) | (buf[2] << 0)
    return VREF * (i / 8388608) / gain

def mcp3564_read_differential_channel_blocking(spi, channel_no):
    # setup mux
    chan_p = (2 * channel_no) & 0x0f
    chan_n = (chan_p + 1) & 0x0f
    buf = [mcp3564_make_cmd(MUX, 'w'), ((chan_p << 4) | (chan_n << 0))]
    spi.xfer(buf)

    # start reading with 'fast command'
    buf = [(1 << 6) | (0b1010 << 2)]
    spi.xfer(buf)

    # poll conversion done flag
    while (True):
        buf = [mcp3564_make_cmd(IRQ, 'r'), 0]
        spi.xfer(buf)
        if (not(buf[1] & (1 << 6))):
            break
        time.sleep(0.001)

    buf = [mcp3564_make_cmd(ADCDATA, 'r'), 0, 0, 0]
    spi.xfer(buf)
    return adc_result_to_voltage(buf[1:])

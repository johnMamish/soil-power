#!/usr/bin/python3
import time
import smbus
import spidev
import ctypes

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
    buf = spi.xfer(buf)
    print(f"SPI recieved:     {''.join([f'{x:02x} ' for x in buf])}")
    print()

def mcp3564_init(spi):
    # Sanity check: read the LOCK register back.
    print("Reading LOCK register:")
    spi_xfer_loud(spi, [mcp3564_make_cmd(LOCK, 'r'), 0])    
    print()
    
    # CONFIG0: use internal oscillator, no current bias, turn on ADC in standby
    buf = [mcp3564_make_cmd(CONFIG0, 'w'), (0b10 << 4) | (0b10 << 0)]
    spi_xfer_loud(spi, buf)

    # CONFIG1: AMCLK = MCLK/2; oversample = 1024 (final data rate of 600Hz)
    buf = [mcp3564_make_cmd(CONFIG1, 'w'), (0b01 << 6) | (0b0101 << 2)]
    spi_xfer_loud(spi, buf)

    # CONFIG2: don't do anything; fine with default settings.

    # setup gaincal.
    # Datasheet says that the error for a gain of 1x is ~+1.8%. Experimentally we found it to be in agreement at ~+1.77%.
    # This value could use further tuning.
    spi_xfer_loud(spi, [mcp3564_make_cmd(GAINCAL, 'w'), 0x7c, 0xab, 0xd8])
    
    # CONFIG3: conversion mode one-shot; default 24-bit ADC format; default CRC settings; OFFSET/GAINCAL enabled
    buf = [mcp3564_make_cmd(CONFIG3, 'w'), (0b10 << 6) | (0b00 << 4) | (1 << 0)]
    spi_xfer_loud(spi, buf)
    
    # Enable IRQ pin; note a quirk with this chip: either the IRQ output must be enabled or the IRQ pin must be
    # pulled up for ADC conversions to work
    buf = [mcp3564_make_cmd(IRQ, 'w'), (0b01 << 2) | (1 << 1) | (1 << 0)]
    spi_xfer_loud(spi, buf)


    spi_xfer_loud(spi, buf)

def adc_result_to_voltage(buf, gain=1.0, VREF = 3.32):
    _bin = "{0:08b}{1:08b}{2:08b}".format(*buf)
    return VREF * (ctypes.c_int32(int((_bin[0] * 8) + _bin, 2)).value / 8388608) / gain

def mcp3564_read_differential_channel_blocking_raw(spi, channel_no):
    # setup mux
    chan_p = (2 * channel_no) & 0x0f
    chan_n = (chan_p + 1) & 0x0f
    buf = [mcp3564_make_cmd(MUX, 'w'), ((chan_p << 4) | (chan_n << 0))]
    spi.xfer(buf)

    # start reading with 'fast command'
    buf = [(1 << 6) | (0b1010 << 2)]
    spi.xfer(buf)

    # poll conversion done flag
    tstart = time.clock_gettime(time.CLOCK_MONOTONIC)
    while (True):
        buf = [mcp3564_make_cmd(IRQ, 'r'), 0]
        buf = spi.xfer(buf)
        if (not(buf[1] & (1 << 6))):
            break
        tnow = time.clock_gettime(time.CLOCK_MONOTONIC)
        if ((tnow - tstart) > 0.01):
            print("warning: conversion timed out")
            return None
        time.sleep(0.001)

    buf = [mcp3564_make_cmd(ADCDATA, 'r'), 0, 0, 0]
    spi.xfer(buf)
    return buf[1:]

def mcp3564_read_differential_channel_blocking(spi, channel_no):
    return adc_result_to_voltage(mcp3564_read_differential_channel_blocking_raw(spi, channel_no))

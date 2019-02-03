sudo apt-get install python-smbus

buffer for read: data = bytearray(2)

Shift to little endian
def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp

the & oxFFFF - python is all in signed 64 bit integers
    - we only care about lower 16 bits, so we mask everything and grab 16
    - 2>4>8>16 - FFFF
Master
 Data goes low, clock goes low
 address in hex 0x48 and then shift left one bit and r(1)/w bit, awk
 awk, data high but device will keep it low.
 - ex: 0x48, w (0), register byte, clock high data high
 - ex: 0x48, r (1),
then one byte of register

Example

import smbus
BUS = 1
ADDRESS = 0x48

bus = smbus.SMBus(BUS)

# read two bytes from register 01, the config reg
config = bus.read_word_data(ADDRESS, 0x01) & 0xFFFF
print('Config value: 0x{0:04X}'.format(config))

# write two bytes to the config register
new_config = 0b0100001110000011
bus.write_word_data(ADDRESS, 0x01, new_config)

# read two bytes from register 00
value = bus.read_word_data(ADDRESS, 0x00) & 0xFFFF
# swap byte order
value = ((value & 0xFF) << 8) | (value >> 8)
print('raw value: 0x{0:04X}'.format(config))

Register Reading:
Dec[25, 26, 27, 28, 35, ]

Config
Notes:
device is in sleep mode at power up
enable DLPF - 1 kHz
25:Sample Rate: 1 kHz/(1+val), dependent on Gyro smpl rate > depends on LPF,
    DLPF == [1-6] -> 1kHz, [0,7] -> 8kHz
    Sample Rate: 0x19 + [0001 0011] - 8 bit, 50 Hz
26: Config is FSync/LPF: 00-- ----, 6 bit, 3 per chapter
    Config: 0x1A + 00[00+0][001] - 2 unused, 2x3 bit. fSync off, 184x2ms
    LPF: ^ in DPF is \/ in f, ^ in delay. 0,7 are 8 kHz.
    1-6> 1: 184 Hz, 2ms
    2: 94f, 3ms
    3: 44f, 4.9ms
    4: 21f, 8.5ms
    5: 10f, 13.8ms
    6: 5f, 19ms
27: Gyro - [x,y,z]self test, [--]full scale select.fs_sel, [000]
    Gyro: 0x1B + [000][0+0][000] - no self test, 250 */s, 3 unused after
    0: 250 */s
    1: 500 */s
    2: 1000 */s
    3: 2000 */s
28: Accel: Same. 0 - 2g, 1 - 4g, 2 - 8g, 3 - 16g.
    Accel: 0x1C + [000][0+1][000]
35: FIFO Config: Temp, GX, GY, GZ, A, slv1, slv2, slv3
    FIFO: 0x23 + [0][1][1][1]+[1][000] - gyro and accel.

55: Interrupt pin - int level, int open, latch en, clear, fsy, fsy, bypass
    Int: 0x37 + [0000+000]0
56: Interrupt enable - Fifo overflow en, i2c master en, data ready en
    Interrupt: 0x38 + 000[1][1]00[1]
58: Interrupt status - r/!w - fifo oflow, 12c master, data ready
    Read interrupt: 0x38 + 000[1]+[1]00[1]

59-64: Accelerometer
    0x3B: Axh
    0x3C: Axl
    0x3D: Ayh
    0x3E: Ayl
    0x3F: Azh
    0x40: Azl

65, 66
    0x41, 0x42: Temp H, L
    C = (TEMP_OUT Register Value as a signed quantity)/340d + 36.53d

67-72: Gyros
    0x43: Gyro X H
    0x44: Gyro X L
    0x45: Gyro y H
    0x46: Gyro y L
    0x47: Gyro z H
    0x48: Gyro z L

106: User Control - 0, fifo-en, i2c mst en, mpu has no SPI,
    0, fifo reset, i2c mst reset, sig cond reset (all registers clear).
    First enable fifo, then send zero's there. must be 0 en, 1 on reset
    User C: 0x6A + 0[1][0]0 + 0[1][0][0]
107 & 108 are power management
    Power 1 - device reset default, sleep, cycle mode, temp disabled, clk
    Power 1: 0x6B + [0][0][0]0 + [1][001]
    clk: internal, x,y,z gyro (1,2,3), externals
    Power 2: low power wake freq (2 bits), stby xa, ya, za, xg, yg, zg
    0x6c + [00][0][0]+[0][0][0][0]
114 and 115 are fifo count:
    This is in bytes of samples contained.
    0x72, 0x73
    114: Fifo High Count - if H read, it updates, 16 bit unsigned together.
116 is fifo r/w, 0x74
    ordered lowest to highest register number. If overflowed, it will
    discard oldest. If empty, you get the last read byte back. Also
    FIFO_OFLOW_INT is set to 1 if this is the case.


[0x6B, 0b10000000] # device reset

user_w = [0x6A, 0b00000000] # fifo off, fifo reset
power1_w = [0x6B, 0b00001001] # temp disabled, clock on gyro x

sample_w = [0x19, 0b00010011]
config_w = [0x1A, 0b00000001]
gyro_w = [0x1B, 0b00000000]
accel_w = [0x1C, 0b00001000]
#fifoc_w = [0x23, 0b01111000]

Read Fifo Count
[0x72]

Burst Read A
[0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40] # xhl, yhl, zhl

Burst Read G
[0x43, 0x44, 0x45, 0x46, 0x47, 0x48] # xhl, yhl, zhl

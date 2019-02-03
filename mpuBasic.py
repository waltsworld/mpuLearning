

# To check connected i2c: sudo i2cdetect -y 1 [bus 1]
# Pull up on SDA and SCL : (Vcc-Vol(0.4))/Iol(3mA)
# Write a single register
# bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x80)

# Check configs
# 25:Sample Rate: 1 kHz/(1+val), dependent on Gyro smpl rate > depends on LPF,
#     DLPF == [1-6] -> 1kHz, [0,7] -> 8kHz
#     Sample Rate: 0x19 + [0001 0011] - 8 bit, 50 Hz
# 26: Config is FSync/LPF: 00-- ----, 6 bit, 3 per chapter
#     Config: 0x1A + 00[00+0][001] - 2 unused, 2x3 bit. fSync off, 184x2ms
#     LPF: ^ in DPF is \/ in f, ^ in delay. 0,7 are 8 kHz.
#     1-6> 1: 184 Hz, 2ms
#     2: 94f, 3ms
#     3: 44f, 4.9ms
#     4: 21f, 8.5ms
#     5: 10f, 13.8ms
#     6: 5f, 19ms
# 27: Gyro - [x,y,z]self test, [--]full scale select.fs_sel, [000]
#     Gyro: 0x1B + [000][0+0][000] - no self test, 250 */s, 3 unused after
#     0: 250 */s
#     1: 500 */s
#     2: 1000 */s
#     3: 2000 */s
# 28: Accel: Same. 0 - 2g, 1 - 4g, 2 - 8g, 3 - 16g.
#     Accel: 0x1C + [000][0+1][000]
# 35: FIFO Config: Temp, GX, GY, GZ, A, slv1, slv2, slv3
#     FIFO: 0x23 + [0][1][1][1]+[1][000] - gyro and accel.

import smbus

BUS = 1
ADD = 0x68
bus = smbus.SMBus(BUS)

# Output

def reset_default():
    if input('Are you Sure? [1,0]'):
        bus.write_byte_data(ADD, 0x6B, 0b10000000)

def sleep_device():
    bus.write_byte_data(ADD, 0x6B, 0b01000000)

def wake_device():
    bus.write_byte_data(ADD, 0x6B, 0b00000000)

def config_check():
    for i in [0x6A, 0x19, 0x1A, 0x1B, 0x1C, 0x23, 0x6B]:
        a = bus.read_byte_data(ADD, i)
        print('0x{0:04X}: 0b{a:08b}'.format(i, a))

def config1():
    print('\nold')
    config_check()
    print('\n\nnew')
    config_w = [
    [0x6A, 0b00000000], # fifo off, fifo reset
    [0x6B, 0b00001001], # temp disabled, clock on gyro x
    [0x19, 0b00010011], # sample rate
    [0x1A, 0b00000001], # fsync and lpf
    [0x1B, 0b00000000], # gyro
    [0x1C, 0b00001000]] # accel

    # Register Writing
    for i in range(len(config_w)):
            bus.write_byte_data(ADD, *config_w[i])
    config_check()

#sample_w = [0x19, 0b00010011]
#config_w = [0x1A, 0b00000001]
#gyro_w = [0x1B, 0b00000000]
#accel_w = [0x1C, 0b00001000]
#fifoc_w = [0x23, 0b01111000]

def get_byte(reg):
    return bus.read_i2c_block_data(ADD, reg) & 0xFF

def get_block():
    return bus.read_i2c_block_data(ADD, 0x3B) & 0xFFFFFF



if __name__ == "__main__":

    print('Bus is: ', BUS)
    print('Add is: ', ADD)

    if bus.read_byte_data(ADD, 0x6B) == 0x40:
        print('It was asleep...')
        bus.write_byte_data(ADD, 0x6B, 0b00000000)
        print('01101001011011010110000101101100' +
        '01101001011101100110010101100101')
    config_check()

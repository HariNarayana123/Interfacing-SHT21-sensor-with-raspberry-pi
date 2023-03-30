import smbus
import time
import RPi.GPIO as GPIO

## SHT21 Temperature

# Initialize the I2C bus
bus = smbus.SMBus(1)

def measure():

    bus.write_byte(0x40, 0xFE) # softreset command
    time.sleep (0.050)
    t = read_temperature()
    rh = read_humidity()
    return (t,rh)

def read_temperature():
        bus.write_byte(0x40, 0xF3)
        time.sleep(0.086)  # wait, typ=66ms, max=85ms @ 14Bit resolution
        data = bus.read_i2c_block_data(0x40, 0xE3, 3)
        #if (check_crc(data, 2)):
        t = ((data[0] << 8) + data[1]) & 0xFFFC  # set status bits to zero
        t = -46.85 + ((t * 175.72) / 65536)  # T = 46.82 + (175.72 * ST/2^16 )
        return round(t, 1)
        #else:
            #return None

def read_humidity():
        """ RH measurement (no hold master), blocking for ~ 32ms !!! """
        bus.write_byte(0x40, 0xF5)  # Trigger RH measurement (no hold master)
        time.sleep(0.03)  # wait, typ=22ms, max=29ms @ 12Bit resolution
        data = bus.read_i2c_block_data(0x40, 0xE5, 3)
        #if (check_crc(data, 2)):
        rh = ((data[0] << 8) + data[1]) & 0xFFFC  # zero the status bits
        rh = -6 + ((125 * rh) / 65536)
        if (rh > 100): rh = 100
        return round(rh, 1)
        #else:
            #return None


def check_crc(data, length):
        """Calculates checksum for n bytes of data and compares it with expected"""
        crc = 0
        for i in range(length):
            crc ^= (ord(chr(data[i])))
            for bit in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x131  # CRC POLYNOMIAL
                else:
                    crc = (crc << 1)
        return True if (crc == data[length]) else False

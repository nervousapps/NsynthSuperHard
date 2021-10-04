# Copyright 2017 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/usr/bin/env python

# Reads the hardware inputs from the MCU and prints them.

import smbus
import struct
import time
from gpiozero import Button

button1 = Button(5)
button2 = Button(6)
button3 = Button(13)
button4 = Button(26)

bus = smbus.SMBus(1)


def test_checksum(data):
    uints = struct.unpack('4I', data)
    chk = 0xaa55aa55
    chk += uints[0]
    chk += uints[1]
    chk += uints[2]
    return (chk & 0xffffffff) == uints[3]


def main():
    address = 0x47

    previous_touch = (-1,-1)
    previous_rots = (-1,-1, -1,-1)
    previous_pots = (-1,-1, -1,-1, -1,-1)

    while True:
        try:
            data = bus.read_i2c_block_data(address, 0, 16)
        except IOError:
            print('did not respond')
            # time.sleep(1)
            continue
        # print(data)
        data = ''.join(map(chr, data))
        # print(data)
        data = data.encode('iso-8859-1')
        # print(data)
        unpacked = struct.unpack('2b4b6BI', data)
        touch = unpacked[:2]
        rots = unpacked[2:6]
        pots = unpacked[6:12]
        chk = unpacked[12]

        if test_checksum(data):
            if touch != previous_touch:
                print(f"touch={touch}")
                previous_touch = touch
            if rots != previous_rots:
                print(f"rots={rots}")
                previous_rots = rots
            if pots != previous_pots:
                print(f"pots={pots}")
                previous_pots = pots
        # print('touch={} rots={} pots={} chk=0x{:08x} {}'.format(
        #    touch, rots, pots, chk,
        #    'passed' if test_checksum(data) else 'failed',
        # ))
        time.sleep(0.01)
        if button1.is_pressed:
            print("Button 1 pressed")
        else:
            # print("Released")
            pass
        if button2.is_pressed:
            print("Button 2 pressed")
        if button3.is_pressed:
            print("Button 3 pressed")
        if button4.is_pressed:
            print("Button 4 pressed")
        time.sleep(0.01)

main()

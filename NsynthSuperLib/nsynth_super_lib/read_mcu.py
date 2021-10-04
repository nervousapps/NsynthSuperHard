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

import asyncio
import smbus
import struct


class ReadMcu:
    """
    Read MCU
    """

    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.touch_queue = asyncio.Queue()
        self.rotary_queue = asyncio.Queue()
        self.potentiometer_queue = asyncio.Queue()

    async def run(self):
        await self._read_mcu()

    def _test_checksum(self, data):
        uints = struct.unpack('4I', data)
        chk = 0xaa55aa55
        chk += uints[0]
        chk += uints[1]
        chk += uints[2]
        return (chk & 0xffffffff) == uints[3]

    async def _read_mcu(self):
        address = 0x47

        previous_touch = (-1, -1)
        previous_rots = (-1, -1, -1, -1)
        previous_pots = (-1, -1, -1, -1, -1, -1)
        # previous_chk = -1

        while True:
            try:
                data = self.bus.read_i2c_block_data(address, 0, 16)
            except IOError:
                print('did not respond')
                continue
            data = ''.join(map(chr, data))
            data = data.encode('iso-8859-1')
            unpacked = struct.unpack('2b4b6BI', data)
            touch = unpacked[:2]
            rots = unpacked[2:6]
            pots = unpacked[6:12]
            chk = unpacked[12]

            if self._test_checksum(data):  # and chk != previous_chk:
                print(f"chk={chk}")
                # previous_chk = chk
                if touch != previous_touch:
                    try:
                        self.touch_queue.put_nowait(touch)
                        print(f"touch={touch}")
                        previous_touch = touch
                    except asyncio.QueueFull as error:
                        print(error)
                if rots != previous_rots:
                    try:
                        self.rotary_queue.put_nowait(rots)
                        print(f"rots={rots}")
                        previous_rots = rots
                    except asyncio.QueueFull as error:
                        print(error)
                if pots != previous_pots:
                    try:
                        self.potentiometer_queue.put_nowait(rots)
                        print(f"pots={pots}")
                        previous_pots = pots
                    except asyncio.QueueFull as error:
                        print(error)

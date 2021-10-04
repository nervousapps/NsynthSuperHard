import asyncio
import concurrent.futures
import smbus2
import struct
import time
from gpiozero import Button


class ReadHardwareInputs:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

        self.running = False
        self.read_mcu_task = None
        self.call_handlers_queue_task = None

        self.queue_touch = asyncio.Queue()

        self.button1 = Button(5)
        self.button2 = Button(6)
        self.button3 = Button(13)
        self.button4 = Button(26)

        self.bus = smbus2.SMBus(1)

    def run(self):
        self.running = True
        with concurrent.futures.ThreadPoolExecutor() as pool:
            read_mcu_thread = self.loop.run_in_executor(
                pool, self.read_mcu)
            self.read_mcu_task = asyncio.ensure_future(
                read_mcu_thread, self.loop)
            self.call_handlers_queue_task = asyncio.ensure_future(
                self.call_handlers_queue, self.loop)

    def stop(self):
        self.running = False
        self.read_mcu_task.cancel()
        self.call_handlers_queue_task.cancel()

    def test_checksum(data):
        uints = struct.unpack('4I', data)
        chk = 0xaa55aa55
        chk += uints[0]
        chk += uints[1]
        chk += uints[2]
        return (chk & 0xffffffff) == uints[3]

    async def read_mcu(self):
        address = 0x47

        previous_touch = (-1, -1)
        previous_rots = (-1, -1, -1, -1)
        previous_pots = (-1, -1, -1, -1, -1, -1)

        while self.running:
            try:
                data = self.bus.read_i2c_block_data(address, 0, 16)
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

            if self.test_checksum(data):
                if touch != previous_touch:
                    self.queue_touch.put_nowait(touch)
                    previous_touch = touch
                if rots != previous_rots:
                    print(f"rots={rots}")
                    previous_rots = rots
                if pots != previous_pots:
                    print(f"pots={pots}")
                    previous_pots = pots

            asyncio.sleep(0.01)
            if self.button1.is_pressed:
                print("Button 1 pressed")
            if self.button2.is_pressed:
                print("Button 2 pressed")
            if self.button3.is_pressed:
                print("Button 3 pressed")
            if self.button4.is_pressed:
                print("Button 4 pressed")
            asyncio.sleep(0.01)

    async def call_handlers_queue(self):
        while self.running:
            touch = self.queue_touch.get()
            if touch:
                print(f"touch={touch}")

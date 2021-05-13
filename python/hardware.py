"""
Hardware class
"""
import asyncio
import time
import smbus
import struct
from gpiozero import Button

BOUNCE = 5.0

class Hardware:
    def __init__(self, b1_cb, b2_cb, b3_cb, b4_cb, inputs_cbs):
        """
        inputs_cbs = (pot1, pot2, pot3, pot4, pot5, pot6, rot1, rot2, rot3, rot4, touchx, touchy)
        """
        self.running = True
        self.pressed = False
        # self.button1 = Button(5, bounce_time=BOUNCE)
        # self.button2 = Button(6, bounce_time=BOUNCE)
        # self.button3 = Button(13, bounce_time=BOUNCE)
        # self.button4 = Button(26, bounce_time=BOUNCE)
        # self.b1_cb = b1_cb
        # self.b2_cb = b2_cb
        # self.b3_cb = b3_cb
        # self.b4_cb = b4_cb
        button_sounds = {
            Button(5, bounce_time=BOUNCE): self.b1_cb,
            Button(6, bounce_time=BOUNCE): self.b2_cb,
            Button(13, bounce_time=BOUNCE): self.b3_cb,
            Button(26, bounce_time=BOUNCE): self.b4_cb
        }
        for button, cb in button_sounds.items():
            button.when_pressed = await cb()



        self.bus = smbus.SMBus(1)

        self.pot1_cb, self.pot2_cb, self.pot3_cb, self.pot4_cb, self.pot5_cb, self.pot6_cb, self.rot1_cb, self.rot2_cb, self.rot3_cb, self.rot4_cb, self.touchx_cb, self.touchy_cb = inputs_cbs

        self.address = 0x47
        try:
            for i in range(3):
                self.previous_data = self.bus.read_i2c_block_data(self.address, 0, 16)
        except IOError:
            print('did not respond')

    def stop(self):
        self.running = False

    def start(self, loop):
        self.running = True
        loop.create_task(self.check_inputs_task())
        loop.create_task(self.check_buttons_task())

    @staticmethod
    def test_checksum(data):
        uints = struct.unpack('4I', data)
        chk = 0xaa55aa55
        chk += uints[0]
        chk += uints[1]
        chk += uints[2]
        return (chk & 0xffffffff) == uints[3]


    async def check_inputs_task(self):
        previous_data = self.previous_data
        print("################ In check inputs task")
        while self.running:
            try:
                data = self.bus.read_i2c_block_data(self.address, 0, 16)
                if data and data != previous_data:
                    # Pot1
                    if data[6] != previous_data[6]:
                        await self.pot1_cb(data[6])
                    # Pot2
                    if data[7] != previous_data[7]:
                        await self.pot2_cb(data[7])
                    # Pot3
                    if data[8] != previous_data[8]:
                        await self.pot3_cb(data[8])
                    # Pot4
                    if data[9] != previous_data[9]:
                        await self.pot4_cb(data[9])
                    # Pot5
                    if data[10] != previous_data[10]:
                        await self.pot5_cb(data[10])
                    # Pot6
                    if data[11] != previous_data[11]:
                        await self.pot6_cb(data[11])
                    # Rot1
                    if data[2] != previous_data[2]:
                        if (data[2] == 0 and previous_data[2] == 255) or data[2] > previous_data[2]:
                            await self.rot1_cb(True)
                        else:
                            await self.rot1_cb(False)
                    # Rot2
                    if data[3] != previous_data[3]:
                        await self.rot2_cb(data[3])
                    # Rot3
                    if data[4] != previous_data[4]:
                        await self.rot3_cb(data[4])
                    # Rot4
                    if data[5] != previous_data[5]:
                        await self.rot4_cb(data[5])
                    # TouchX
                    if data[0] != previous_data[0]:
                        await self.touchx_cb(data[0])
                    # TouchY
                    if data[1] != previous_data[1]:
                        await self.touchy_cb(data[1])
                    # for index, value in enumerate(data):
                    #     if previous_data and value != previous_data[index]:
                    #         print(f"Data {index} : {value}")
                    previous_data = data
                    # await self.inputs_cb(data)
                await asyncio.sleep(0.05)
            except IOError:
                print('did not respond')
                await asyncio.sleep(1)
            except Exception as error:
                print(f"Inputs task : {error}")
                await asyncio.sleep(1)

    async def check_buttons_task(self):
        print("################ In check buttons task")
        # while self.running:
        #     try:
        #         if self.button1.is_pressed:
        #           print("Pressed")
        #           await self.b1_cb()
        #         if self.button2.is_pressed:
        #           print("Pressed")
        #           await self.b2_cb()
        #         if self.button3.is_pressed:
        #           print("Pressed")
        #           await self.b3_cb()
        #         if self.button4.is_pressed:
        #           print("Pressed")
        #           await self.b4_cb()
        #         await asyncio.sleep(0.05)
        #     except Exception as error:
        #         print(f"Buttons task : {error}")
        #         await asyncio.sleep(1)

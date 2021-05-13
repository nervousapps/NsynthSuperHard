"""
Hardware class
"""
import asyncio
import concurrent.futures
import time
import smbus
import struct
from gpiozero import Button

BOUNCE = 5.0

class Hardware:
    def __init__(self, loop, b1_cb, b2_cb, b3_cb, b4_cb, inputs_cbs):
        """
        inputs_cbs = (pot1, pot2, pot3, pot4, pot5, pot6, rot1, rot2, rot3, rot4, touchx, touchy)
        """
        self.loop = loop
        self.running = True
        self.pressed = False
        self.button1 = Button(5, bounce_time=BOUNCE)
        self.button2 = Button(6, bounce_time=BOUNCE)
        self.button3 = Button(13, bounce_time=BOUNCE)
        self.button4 = Button(26, bounce_time=BOUNCE)
        self.b1_cb = b1_cb
        self.b2_cb = b2_cb
        self.b3_cb = b3_cb
        self.b4_cb = b4_cb
        # button_sounds = {
        #     Button(5, bounce_time=BOUNCE): b1_cb,
        #     Button(6, bounce_time=BOUNCE): b2_cb,
        #     Button(13, bounce_time=BOUNCE): b3_cb,
        #     Button(26, bounce_time=BOUNCE): b4_cb
        # }
        # for button, cb in button_sounds.items():
        #     button.when_pressed = cb



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

    def start(self):
        self.running = True
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = asyncio.ensure_future(self.loop.run_in_executor(
                pool, self.check_inputs_task))
            print('custom input thread pool', result)
            result = asyncio.ensure_future(self.loop.run_in_executor(
                pool, self.check_buttons_task))
            print('custom button thread pool', result)
        # self.loop.create_task(self.check_inputs_task())
        # self.loop.create_task(self.check_buttons_task())

    def check_inputs_task(self):
        previous_data = self.previous_data
        print("################ In check inputs task")
        while self.running:
            try:
                data = self.bus.read_i2c_block_data(self.address, 0, 16)
                if data and data != previous_data:
                    # Pot1
                    if data[6] != previous_data[6]:
                        print(f"################ Pot 1 : {data[6]}")
                        asyncio.run_coroutine_threadsafe(self.pot1_cb(data[6]), self.loop).result()
                    # Pot2
                    if data[7] != previous_data[7]:
                        asyncio.run_coroutine_threadsafe(self.pot2_cb(data[7]), self.loop).result()
                    # Pot3
                    if data[8] != previous_data[8]:
                        asyncio.run_coroutine_threadsafe(self.pot3_cb(data[8]), self.loop).result()
                    # Pot4
                    if data[9] != previous_data[9]:
                        asyncio.run_coroutine_threadsafe(self.pot4_cb(data[9]), self.loop).result()
                    # Pot5
                    if data[10] != previous_data[10]:
                        asyncio.run_coroutine_threadsafe(self.pot5_cb(data[10]), self.loop).result()
                    # Pot6
                    if data[11] != previous_data[11]:
                        asyncio.run_coroutine_threadsafe(self.pot6_cb(data[11]), self.loop).result()
                    # Rot1
                    if data[2] != previous_data[2]:
                        if (data[2] == 0 and previous_data[2] == 255) or data[2] > previous_data[2]:
                            asyncio.run_coroutine_threadsafe(self.rot1_cb(True), self.loop).result()
                        else:
                            asyncio.run_coroutine_threadsafe(self.rot1_cb(False), self.loop).result()
                    # Rot2
                    if data[3] != previous_data[3]:
                        asyncio.run_coroutine_threadsafe(self.rot2_cb(data[3]), self.loop).result()
                    # Rot3
                    if data[4] != previous_data[4]:
                        asyncio.run_coroutine_threadsafe(self.rot3_cb(data[4]), self.loop).result()
                    # Rot4
                    if data[5] != previous_data[5]:
                        asyncio.run_coroutine_threadsafe(self.rot4_cb(data[5]), self.loop).result()
                    # TouchX
                    if data[0] != previous_data[0]:
                        asyncio.run_coroutine_threadsafe(self.touchx_cb(data[0]), self.loop).result()
                    # TouchY
                    if data[1] != previous_data[1]:
                        asyncio.run_coroutine_threadsafe(self.touchy_cb(data[1]), self.loop).result()
                    # for index, value in enumerate(data):
                    #     if previous_data and value != previous_data[index]:
                    #         print(f"Data {index} : {value}")
                    previous_data = data
                    # await self.inputs_cb(data)
                # await asyncio.sleep(0.05)
                time.sleep(0.1)
            except IOError:
                print('did not respond')
                # await asyncio.sleep(1)
            except Exception as error:
                print(f"Inputs task : {error}")
                # await asyncio.sleep(1)

    def check_buttons_task(self):
        print("################ In check buttons task")
        while self.running:
            print("################ In check buttons task")
            try:
                if self.button1.is_held:
                  print(f"Hold time : {self.button1.held_time}")
                  asyncio.run_coroutine_threadsafe(self.b1_cb(), self.loop).result()
                if self.button2.is_pressed:
                  print("Pressed")
                  asyncio.run_coroutine_threadsafe(self.b2_cb(), self.loop).result()
                if self.button3.is_pressed:
                  print("Pressed")
                  asyncio.run_coroutine_threadsafe(self.b3_cb(), self.loop).result()
                if self.button4.is_pressed:
                  print("Pressed")
                  asyncio.run_coroutine_threadsafe(self.b4_cb(), self.loop).result()
                # await asyncio.sleep(0.05)
                time.sleep(0.1)
            except Exception as error:
                print(f"Buttons task : {error}")
                # await asyncio.sleep(1)

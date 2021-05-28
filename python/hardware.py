"""
Hardware class
"""
import asyncio
import concurrent.futures
import smbus
import time
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device, Button


BOUNCE = 5


class Hardware:
    """
    Drive the OpenNsynthSuper hardware (encoders, pushbuttons, touch panel and potentiometers)
    """

    def __init__(self, loop, b1_cb, b2_cb, b3_cb, b4_cb, inputs_cbs):
        """
        bX_cb = bX_cb, bXh_cb
        inputs_cbs = (pot1, pot2, pot3, pot4, pot5, pot6, rot1, rot2, rot3, rot4, touch)
        """
        Device.pin_factory = PiGPIOFactory()
        self.loop = loop
        self.running = True
        self.pressed = False
        self.task = None

        self.b1_cb, self.b1h_cb = b1_cb
        self.b2_cb, self.b2h_cb = b2_cb
        self.b3_cb, self.b3h_cb = b3_cb
        self.b4_cb, self.b4h_cb = b4_cb

        self.button1 = Button(5)
        self.button2 = Button(6)
        self.button3 = Button(13)
        self.button4 = Button(26)

        self.button1.hold_time = 2
        self.button2.hold_time = 2
        self.button3.hold_time = 2
        self.button4.hold_time = 2

        self.button1.when_pressed = self.button_pressed_cb
        self.button2.when_pressed = self.button_pressed_cb
        self.button3.when_pressed = self.button_pressed_cb
        self.button4.when_pressed = self.button_pressed_cb

        self.button1.when_held = self.button_held_cb
        self.button2.when_held = self.button_held_cb
        self.button3.when_held = self.button_held_cb
        self.button4.when_held = self.button_held_cb

        self.bus = smbus.SMBus(1)

        self.pot1_cb, self.pot2_cb, self.pot3_cb, self.pot4_cb, self.pot5_cb, \
            self.pot6_cb, self.rot1_cb, self.rot2_cb, self.rot3_cb, \
            self.rot4_cb, self.touch_cb = inputs_cbs

        self.address = 0x47
        try:
            for i in range(3):
                self.previous_data = self.bus.read_i2c_block_data(self.address,
                                                                  0,
                                                                  16)
                break
        except IOError:
            print('did not respond')

    def button_pressed_cb(self, device):
        if device == self.button1 and self.b1_cb:
            self.loop.call_soon_threadsafe(self.b1_cb)
        elif device == self.button2 and self.b2_cb:
            self.loop.call_soon_threadsafe(self.b2_cb)
        elif device == self.button3 and self.b3_cb:
            self.loop.call_soon_threadsafe(self.b3_cb)
        elif device == self.button4 and self.b4_cb:
            self.loop.call_soon_threadsafe(self.b4_cb)

    def button_held_cb(self, device):
        if device == self.button1 and self.b1_cb:
            self.loop.call_soon_threadsafe(self.b1h_cb)
        elif device == self.button2 and self.b2h_cb:
            self.loop.call_soon_threadsafe(self.b2h_cb)
        elif device == self.button3 and self.b3h_cb:
            self.loop.call_soon_threadsafe(self.b3h_cb)
        elif device == self.button4 and self.b4h_cb:
            self.loop.call_soon_threadsafe(self.b4h_cb)

    def stop(self):
        self.running = False

    def start(self):
        self.running = True

    def check_inputs_task(self):
        previous_data = self.previous_data
        previous_datax = None
        previous_datay = None
        print("################ In check inputs task")
        while(True):
            while self.running:
                try:
                    datax = None
                    datay = None
                    data = self.bus.read_i2c_block_data(self.address, 0, 16)
                    if data and data != previous_data:
                        # print(data)
                        # Pot1
                        if data[6] != previous_data[6] and self.pot1_cb:
                            self.loop.call_soon_threadsafe(self.pot1_cb, data[6])
                        # Pot2
                        if data[7] != previous_data[7] and self.pot2_cb:
                            self.loop.call_soon_threadsafe(self.pot2_cb, data[7])
                        # Pot3
                        if data[8] != previous_data[8] and self.pot3_cb:
                            self.loop.call_soon_threadsafe(self.pot3_cb, data[8])
                        # Pot4
                        if data[9] != previous_data[9] and self.pot4_cb:
                            self.loop.call_soon_threadsafe(self.pot4_cb, data[9])
                        # Pot5
                        if data[10] != previous_data[10] and self.pot5_cb:
                            self.loop.call_soon_threadsafe(self.pot5_cb, data[10])
                        # Pot6
                        if data[11] != previous_data[11] and self.pot6_cb:
                            self.loop.call_soon_threadsafe(self.pot6_cb, data[11])
                        # Rot1
                        if data[2] != previous_data[2] and self.rot1_cb:
                            if (data[2] == 0 and previous_data[2] == 255) or \
                               data[2] > previous_data[2]:
                                self.loop.call_soon_threadsafe(self.rot1_cb, True)
                            else:
                                self.loop.call_soon_threadsafe(self.rot1_cb, False)
                        # Rot2
                        if data[3] != previous_data[3] and self.rot2_cb:
                            if (data[3] == 0 and previous_data[3] == 255) or \
                               data[3] > previous_data[3]:
                                self.loop.call_soon_threadsafe(self.rot2_cb, True)
                            else:
                                self.loop.call_soon_threadsafe(self.rot2_cb, False)
                        # Rot3
                        if data[4] != previous_data[4] and self.rot3_cb:
                            self.loop.call_soon_threadsafe(self.rot3_cb, data[4])
                        # Rot4
                        if data[5] != previous_data[5] and self.rot4_cb:
                            self.loop.call_soon_threadsafe(self.rot4_cb, data[5])
                        # Touch
                        if data[0] != previous_data[0] and data[0]:
                            if data[0] == 255:
                                datax = previous_datax
                            else:
                                datax = data[0]
                                previous_datax = datax
                        if data[1] != previous_data[1]:
                            if data[1] in [255, 8]:
                                datay = previous_datay
                            else:
                                datay = data[1]
                                previous_datay = datay
                        if datax or datay:
                            self.loop.call_soon_threadsafe(
                                self.touch_cb,
                                [datax if datax else previous_datax,
                                 datay if datay else previous_datay])
                        previous_data = data
                    time.sleep(0.1)
                    # await asyncio.sleep(0.1)
                except IOError:
                    print('did not respond')
                    # await asyncio.sleep(1)
                except Exception as error:
                    print(f"Inputs task : {error}")
                    # await asyncio.sleep(1)
            while not self.running:
                time.sleep(0.5)

"""
Hardware driver class
"""
import asyncio
import concurrent.futures
import smbus
import time

from . import Encoders, ReadMcu


class HardwareDriver:
    """
    Drive the OpenNsynthSuper hardware (encoders, pushbuttons, touch panel and potentiometers)
    """

    def __init__(self,
                 loop: asyncio.BaseEventLoop,
                 pool: concurrent.futures.ThreadPoolExecutor):
        """

        """
        self.loop = loop
        self.pool = pool

        self.read_mcu = ReadMcu()
        self.encoders = Encoders(self.read_mcu.rotary_queue)

    def launch_drivers(self):
        read_mcu_task = self.loop.run_in_executor(self.pool, self.read_mcu.run)
        encoder_task = self.loop.run_in_executor(self.pool, self.read_mcu.run)
        return asyncio.gather(
            read_mcu_task,
            encoder_task)

    def touch_callback(self, index: int, callback):
        self.touch_callback = callback
        return True

    def set_button_pressed_callback(self, index: int, callback):
        if index < 4:
            self.buttons_pressed_callback[index] = callback
            return True
        return False

    def set_button_held_callback(self, index: int, callback):
        if index < 4:
            self.buttons_held_callback[index] = callback
            return True
        return False

    def set_rotary_callback(self, index: int, callback):
        if index < 4:
            self.rotary_callback[index] = callback
            return True
        return False

    def stop(self):
        self.running = False

    def start(self):
        self.running = True

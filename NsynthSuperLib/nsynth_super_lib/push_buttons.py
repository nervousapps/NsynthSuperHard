from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device, Button


class PushButtons:
    """
    Class to handle all push buttons change
    """

    def __init__(self):
        Device.pin_factory = PiGPIOFactory()
        self.BOUNCE = 5

        # Define buttons
        self.button1 = Button(5)
        self.button2 = Button(6)
        self.button3 = Button(13)
        self.button4 = Button(26)

        self.buttons_pressed_callback = []
        self.buttons_held_callback = []

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

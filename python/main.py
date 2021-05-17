import os
import time
import asyncio
import jack

from hardware import Hardware
from screen import Screen
from midi import Midi

from bristol import Bristol
from fluidsynthwrapper import FluidSynthWrapper


class Main:
    def __init__(self, loop):
        self.loop = loop

        # Get the list of available synths
        self.available_synths = [
            {"name": "BRISTOL", "class": Bristol},
            {"name": "FluidSynth", "class": FluidSynthWrapper}
        ]

        self.screen = Screen()

        self.reload = False
        self.loading = self.screen.get_loading()
        self.synth_index = 1
        self.current_synth = None
        self.menu_line = ["", self.available_synths[self.synth_index]["name"], self.available_synths[self.synth_index-1]["name"]]

        self.pressed = False

        self.hardware = Hardware(self.loop,
                                 self.b_handler,
                                 self.null_button_handler,
                                 self.null_button_handler,
                                 self.null_button_handler,
                                 (self.null_handler, #self.pot1_handler,
                                  self.null_handler, #self.pot2_handler,
                                  self.null_handler, #self.pot3_handler,
                                  self.null_handler, #self.pot4_handler,
                                  self.null_handler, #self.pot5_handler,
                                  self.null_handler, #self.pot6_handler,
                                  self.rot_handler,
                                  self.null_handler, #self.rot2_handler,
                                  self.null_handler, #self.rot3_handler,
                                  self.null_handler, #self.rot4_handler,
                                  self.null_handler, #self.touchx_handler,
                                  self.null_handler)) #self.touchy_handler))
        self.midi = Midi()
        # Init jack client
        self.client = jack.Client('JackClient')

    async def b_handler(self):
        self.hardware.b1_cb = self.b_handler
        self.hardware.b2_cb = self.null_button_handler
        self.hardware.b3_cb = self.null_button_handler
        self.hardware.b4_cb = self.null_button_handler
        self.hardware.pot1_cb = self.null_handler
        self.hardware.pot2_cb = self.null_handler
        self.hardware.pot3_cb = self.null_handler
        self.hardware.pot4_cb = self.null_handler
        self.hardware.pot5_cb = self.null_handler
        self.hardware.pot6_cb = self.null_handler
        self.hardware.rot1_cb = self.rot_handler
        self.hardware.rot2_cb = self.null_handler
        self.hardware.rot3_cb = self.null_handler
        self.hardware.rot4_cb = self.null_handler
        self.hardware.touchx_cb = self.null_handler
        self.hardware.touchy_cb  = self.null_handler
        print(f"Button main handler")
        if self.current_synth:
            self.current_synth.stop()
            self.current_synth = None
        self.pressed = True

    async def null_button_handler(self):
        pass

    async def null_handler(self, data):
        pass

    # TODO : add rotary handlers:
    #    - up-left   : general synth select
    #    - up-right  : selected/running synth menu
    #    - down-right: select x touch CC / push -> select ???
    #    - down-left : select y touch CC / push -> select CC num for each pot
    #                   => add pots handler to send CC value
    async def rot_handler(self, data):
        if data:
            self.synth_index = 0
            self.menu_line = ["", self.available_synths[self.synth_index]["name"], self.available_synths[self.synth_index+1]["name"]]
        else:
            self.synth_index = 1
            self.menu_line = ["", self.available_synths[self.synth_index]["name"], self.available_synths[self.synth_index-1]["name"]]
        print(data)
        print(self.synth_index)
        self.screen.draw_menu(self.menu_line)

    async def main(self):
        try:
            self.screen.draw_text_box("NsynthSuperHard")
            await asyncio.sleep(2)
            self.loop.create_task(self.screen.start_gif(self.loading))

            # self.loop.create_task(self.midi.midi_over_uart_task())
            with self.client:
                await asyncio.sleep(5)
                result = os.popen(f"a2jmidid -e")
                self.screen.stop_gif()
                await asyncio.sleep(2)
                self.screen.draw_menu(self.menu_line)
                self.hardware.start()
                while True:
                    try:
                        if self.pressed:
                            self.pressed = False
                            self.hardware.stop()
                            self.current_synth = self.available_synths[self.synth_index]["class"](
                                                              hardware=self.hardware,
                                                              midi=self.midi,
                                                              screen=self.screen,
                                                              loop=self.loop,
                                                              jack_client=self.client)
                            print("############# Synth created")
                            await self.current_synth.start()
                            self.screen.draw_menu(self.menu_line)
                            await asyncio.sleep(1)
                            if not self.hardware.running:
                                self.hardware.start()
                    except Exception as error:
                        self.screen.stop_gif()
                        print(f"Main loop exception :{error}")
                        self.screen.draw_text_box('Main loop exception !')
                        await asyncio.sleep(2)
                        if self.current_synth:
                            self.current_synth.stop()
                            self.current_synth = None
                        self.pressed = False
                    await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            self.midi.stop()
            self.hardware.stop()
            self.screen.stop()
            self.loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Main(loop).main())

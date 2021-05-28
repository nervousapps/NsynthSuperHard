import os
import time
import asyncio
import concurrent.futures
import jack

from hardware import Hardware
from screen import Screen
from midi import Midi

from bristol_wrapper import BristolWrapper
from fluidsynth_wrapper import FluidSynthWrapper


class Main:
    def __init__(self, loop):
        self.loop = loop

        # Get the list of available synths
        self.available_synths = [
            {"name": "BRISTOL", "class": BristolWrapper},
            {"name": "FluidSynth", "class": FluidSynthWrapper}
        ]

        self.screen = Screen()

        self.reload = False
        self.loading = self.screen.get_loading()
        self.synth_index = 1
        self.current_synth = None
        self.menu_line = ["", self.available_synths[self.synth_index]["name"], self.available_synths[self.synth_index-1]["name"]]

        self.pressed = False

        # Init hardware with appropriate callbacks
        self.hardware = Hardware(self.loop,
                                 (self.b1_handler, self.b1h_handler),
                                 (None, None),
                                 (self.b3_handler, self.b3h_handler),
                                 (self.b4_handler, self.b4h_handler),
                                 (self.pot1_handler,
                                  self.pot2_handler,
                                  self.pot3_handler,
                                  self.pot4_handler,
                                  self.pot5_handler,
                                  self.pot6_handler,
                                  self.rot1_handler,
                                  None, #self.rot2_handler,
                                  self.rot3_handler,
                                  self.rot4_handler,
                                  self.touch_handler))

        # Init the CC values object
        self.ccs = {
            "pot1": 0,
            "pot2": 1,
            "pot3": 2,
            "pot4": 3,
            "pot5": 4,
            "pot6": 5,
            "touchx": 6,
            "touchy": 7,
        }
        self.param_pots = False
        self.select_pot = False
        self.current_pot = 1

        # Init MIDI
        self.midi = Midi()
        self.available_midi_devices = []
        self.param_midi = False
        self.select_midi_device = 0
        self.current_midi_device = self.select_midi_device
        # Init jack client
        self.client = jack.Client('JackClient')

    def b1h_handler(self):
        self.param_midi = not self.param_midi
        if self.param_midi and self.available_midi_devices:
            self.menu_line = []
            for idx, device in enumerate(self.available_midi_devices):
                if idx > 2:
                    break
                self.menu_line.append(device.name)
            if len(self.menu_line) < 3:
                while len(self.menu_line) < 3:
                    self.menu_line.append("")
            self.screen.draw_menu(self.menu_line)
        else:
            pass

    def b3h_handler(self):
        if self.param_pots:
            self.screen.draw_text_box(f"touchy : {self.ccs['touchy']}")
        else:
            self.select_pot = True
            self.screen.draw_text_box(f"pot{self.current_pot}")
        self.param_pots = not self.param_pots

    def b4h_handler(self):
        if self.param_pots:
            self.screen.draw_text_box(f"touchy : {self.ccs['touchy']}")
        else:
            self.select_pot = True
            self.screen.draw_text_box(f"pot{self.current_pot}")
        self.param_pots = not self.param_pots

    def b1_handler(self):
        # if self.param_midi:
        #     self.current_midi_device = self.select_midi_device
        # else:
        print(f"Button main handler")
        if self.current_synth:
            self.current_synth.stop()
            self.current_synth = None
            self.hardware.b1_cb = self.b1_handler
            self.hardware.b2_cb = None
            self.hardware.b3_cb = self.b3_handler
            self.hardware.b4_cb = self.b4_handler
            self.hardware.b1h_cb = self.b1h_handler
            self.hardware.b2h_cb = None
            self.hardware.b3h_cb = self.b3h_handler
            self.hardware.b4h_cb = self.b4h_handler
            self.hardware.pot1_cb = self.pot1_handler
            self.hardware.pot2_cb = self.pot2_handler
            self.hardware.pot3_cb = self.pot3_handler
            self.hardware.pot4_cb = self.pot4_handler
            self.hardware.pot5_cb = self.pot5_handler
            self.hardware.pot6_cb = self.pot6_handler
            self.hardware.rot1_cb = self.rot1_handler
            self.hardware.rot2_cb = None
            self.hardware.rot3_cb = self.rot3_handler
            self.hardware.rot4_cb = self.rot4_handler
            self.hardware.touch_cb = self.touch_handler
        self.pressed = True

    def b3_handler(self):
        if self.param_pots:
            self.select_pot = not self.select_pot
            if self.select_pot:
                self.screen.draw_text_box(f"pot{self.current_pot}")
            else:
                self.screen.draw_text_box(f"pot{self.current_pot} : {self.ccs[f'pot{self.current_pot}']}")
        else:
            pass

    def b4_handler(self):
        if self.param_pots:
            self.select_pot = not self.select_pot
            if self.select_pot:
                self.screen.draw_text_box(f"pot{self.current_pot}")
            else:
                self.screen.draw_text_box(f"pot{self.current_pot} : {self.ccs[f'pot{self.current_pot}']}")
        else:
            pass

    # TODO : add rotary handlers:
    #    - up-left   : general synth select
    #    - up-right  : selected/running synth menu
    #    - down-right: select x touch CC / push -> select ???
    #    - down-left : select y touch CC / push -> select CC num for each pot
    #                   => add pots handler to send CC value
    def rot1_handler(self, data):
        if self.param_midi:
            if data:
                self.select_midi_device += 1
            else:
                self.select_midi_device -= 1
            if self.select_midi_device > len(self.available_midi_devices)-1:
                self.select_midi_device = 0
            elif self.select_midi_device < 0:
                self.select_midi_device = len(self.available_midi_devices)-1
            self.menu_line = ["", self.available_midi_devices[self.select_midi_device].name, ""]
            self.screen.draw_menu(self.menu_line)
        else:
            if data:
                self.synth_index = 0
                self.menu_line = ["", self.available_synths[self.synth_index]["name"], self.available_synths[self.synth_index+1]["name"]]
            else:
                self.synth_index = 1
                self.menu_line = ["", self.available_synths[self.synth_index]["name"], self.available_synths[self.synth_index-1]["name"]]
            print(data)
            print(self.synth_index)
            self.screen.draw_menu(self.menu_line)

    def rot3_handler(self, data):
        if self.param_pots:
            if self.select_pot:
                self.current_pot = int((data/255)*6)
                self.screen.draw_text_box(f"pot{self.current_pot}")
            else:
                self.ccs[f"pot{self.current_pot}"] = int(data/2)
                self.screen.draw_text_box(f"pot{self.current_pot} : {self.ccs[f'pot{self.current_pot}']}")
        else:
            self.ccs["touchx"] = int(data/2)
            self.screen.draw_text_box(f"touchx : {self.ccs['touchx']}")

    def rot4_handler(self, data):
        if self.param_pots:
            pass
        else:
            self.ccs["touchy"] = int(data/2)
            self.screen.draw_text_box(f"touchy : {self.ccs['touchy']}")

    def pot1_handler(self, data):
        self.screen.draw_text_box(f"Pot1 {self.ccs['pot1']}: {int(data/2)}")
        if self.current_synth:
            self.current_synth.cc(0, self.ccs["pot1"], int(data/2))

    def pot2_handler(self, data):
        self.screen.draw_text_box(f"Pot2 {self.ccs['pot2']}: {int(data/2)}")
        if self.current_synth:
            self.current_synth.cc(0, self.ccs["pot2"], int(data/2))

    def pot3_handler(self, data):
        self.screen.draw_text_box(f"Pot3 {self.ccs['pot3']}: {int(data/2)}")
        if self.current_synth:
            self.current_synth.cc(0, self.ccs["pot3"], int(data/2))

    def pot4_handler(self, data):
        self.screen.draw_text_box(f"Pot4 {self.ccs['pot4']}: {int(data/2)}")
        if self.current_synth:
            self.current_synth.cc(0, self.ccs["pot4"], int(data/2))

    def pot5_handler(self, data):
        self.screen.draw_text_box(f"Pot5 {self.ccs['pot5']}: {int(data/2)}")
        if self.current_synth:
            self.current_synth.cc(0, self.ccs["pot5"], int(data/2))

    def pot6_handler(self, data):
        self.screen.draw_text_box(f"Pot6 {self.ccs['pot6']}: {int(data/2)}")
        if self.current_synth:
            self.current_synth.cc(0, self.ccs["pot6"], int(data/2))

    def touch_handler(self, data):
        self.screen.draw_text_box(f"touchx {self.ccs['touchx']}: {int(data[0])} \n touchy {self.ccs['touchy']}: {int(data[1])}")
        if self.current_synth:
            self.current_synth.cc(0, self.ccs["touchx"], int(data[0]))
            self.current_synth.cc(0, self.ccs["touchy"], int(data[1]))

    async def main(self):
        try:
            self.hardware.stop()
            self.screen.draw_text_box("NsynthSuperHard")
            await asyncio.sleep(1)
            # self.loop.create_task(self.screen.start_gif(self.loading))

            # self.loop.create_task(self.midi.midi_over_uart_task())
            with self.client:
                await asyncio.sleep(5)
                _ = os.popen(f"a2jmidid -e")
                await asyncio.sleep(2)
                self.available_midi_devices = self.client.get_ports(
                    is_midi=True, is_output=True)
                self.screen.stop_gif()
                self.screen.draw_menu(self.menu_line)
                self.hardware.start()
                while True:
                    try:
                        if self.pressed and not self.current_synth:
                            self.hardware.stop()
                            self.pressed = False
                            self.current_synth = self.available_synths[self.synth_index]["class"](
                                                              hardware=self.hardware,
                                                              midi=self.midi,
                                                              screen=self.screen,
                                                              loop=self.loop,
                                                              jack_client=self.client)
                            print("############# Synth created")
                            await self.current_synth.start()
                            await asyncio.sleep(1)
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
    main_app = Main(loop)
    with concurrent.futures.ThreadPoolExecutor() as pool:
        hardware_task = loop.run_in_executor(
            pool, main_app.hardware.check_inputs_task)
        loading_task = loop.run_in_executor(
            pool, main_app.screen.start_gif, main_app.loading)
        loop.run_until_complete(asyncio.wait([loading_task,
                                              main_app.main(),
                                              hardware_task]))

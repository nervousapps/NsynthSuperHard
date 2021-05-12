import os
import time
import asyncio
import jack

from hardware import Hardware
from screen import Screen
from midi import Midi


class BristolSynth:
    def __init__(self, loop):
        self.loop = loop

        # Get the list of available synths
        self.available_synths = [
            "mini",
            "explorer"
            "voyager",
            "memory",
            "sonic6",
            "mg1",
            "hammond",
            "b3",
            "prophet",
            "pro52",
            "pro10",
            "pro1",
            "rhodes",
            "rhodesbass",
            "roadrunner",
            "bitone",
            "bit99",
            "bit100",
            "stratus",
            "trilogy",
            "obx",
            "obxa",
            "axxe",
            "odyssey",
            "arp2600",
            "solina",
            "polysix",
            "poly800",
            "monopoly",
            "ms20",
            "vox",
            "voxM2",
            "juno",
            "jupiter",
            "bme700",
            "bm",
            "dx",
            "cs80",
            "sidney",
            "melbourne",
            "granular",
            "aks",
            "mixer"
        ]

        # Init jack client
        self.client = jack.Client('MyGreatClient')

        self.current_synth_index = 0
        self.synth_index = self.current_synth_index
        self.current_synth = self.available_synths[self.current_synth_index]
        self.menu_line = (self.available_synths[-1], self.available_synths[self.synth_index], self.available_synths[self.synth_index+1])

        self.reload = False

        self.screen = Screen()
        self.hardware = Hardware(self.b1_handler,
                                 self.null_handler,
                                 self.null_handler,
                                 self.null_handler,
                                 (self.null_handler, #self.pot1_handler,
                                  self.null_handler, #self.pot2_handler,
                                  self.null_handler, #self.pot3_handler,
                                  self.null_handler, #self.pot4_handler,
                                  self.null_handler, #self.pot5_handler,
                                  self.null_handler, #self.pot6_handler,
                                  self.rot1_handler,
                                  self.null_handler, #self.rot2_handler,
                                  self.null_handler, #self.rot3_handler,
                                  self.null_handler, #self.rot4_handler,
                                  self.null_handler, #self.touchx_handler,
                                  self.null_handler)) #self.touchy_handler))
        self.midi = Midi()

        self.loading = self.screen.get_loading()

    async def start_bristol_emu(self):
        self.loop.create_task(self.screen.start_gif(self.loading))
        print("Stopping bristol")
        result = os.popen(f"startBristol -exit &")
        while self.client.get_all_connections(self.client.get_ports(is_input=True, is_audio=True, name_pattern='playback')[0]) or \
            self.client.get_all_connections(self.client.get_ports(is_input=True, is_audio=True, name_pattern='playback')[1]):
            await asyncio.sleep(0.5)
        self.current_synth = self.available_synths[self.current_synth_index]
        result = os.popen(f"startBristol -{self.current_synth} -jack -autoconn &")
        while not self.client.get_all_connections(self.client.get_ports(is_input=True, is_audio=True, name_pattern='playback')[0]) or \
            not self.client.get_all_connections(self.client.get_ports(is_input=True, is_audio=True, name_pattern='playback')[1]):
            await asyncio.sleep(0.5)
        while not self.client.get_all_connections(self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)[0]):
            self.client.connect(self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)[0],
                                self.client.get_ports(is_midi=True, name_pattern='bristol', is_input=True)[0])
            await asyncio.sleep(0.5)
        self.screen.stop_gif()
        self.screen.draw_text(f"Ready to go !")
        await asyncio.sleep(2)
        self.reload = False
        self.screen.draw_menu(self.menu_line)
        self.hardware.start(self.loop)
        print("Ready to go !")

    async def b1_handler(self):
        self.current_synth_index = self.synth_index
        print(f"Button handler : {self.current_synth_index}")
        self.reload = True
        self.hardware.stop()
        self.midi.stop()

    async def null_handler(self, data):
        pass

    async def rot1_handler(self, data):
        if data:
            self.synth_index = self.synth_index + 1 if self.synth_index < len(self.available_synths)-2 else 0
            self.menu_line = (self.available_synths[self.synth_index+1], self.available_synths[self.synth_index], self.available_synths[self.synth_index-1])
        else:
            self.synth_index = self.synth_index - 1 if self.synth_index > 0 else len(self.available_synths)-2
            self.menu_line = (self.available_synths[self.synth_index-1], self.available_synths[self.synth_index], self.available_synths[self.synth_index+1])
        self.screen.draw_menu(self.menu_line)

    async def main(self):
        try:
            self.screen.draw_text_box("NsynthSuperHard")

            # self.loop.create_task(self.midi.midi_over_uart_task())

            with self.client:
                await asyncio.sleep(1)
                result = os.popen(f"a2jmidid -e")
                await asyncio.sleep(1)
                try:
                    await asyncio.wait_for(self.start_bristol_emu(), timeout=10.0)
                except asyncio.TimeoutError:
                    print('timeout!')
                    self.screen.draw_text_box(f"{self.current_synth} is not available ...")
                    await asyncio.sleep(2)
                while True:
                    if self.current_synth != self.available_synths[self.current_synth_index] or self.reload:
                        try:
                            await asyncio.wait_for(self.start_bristol_emu(), timeout=10.0)
                        except asyncio.TimeoutError:
                            print('timeout!')
                            self.screen.draw_text_box(f"{self.current_synth} is not available ...")
                            await asyncio.sleep(2)
                    await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            self.midi.stop()
            self.hardware.stop()
            self.screen.stop()
            self.loop.close()
            result = os.popen("startBristol -exit &")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(BristolSynth(loop).main())

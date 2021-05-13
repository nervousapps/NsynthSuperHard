import os
import asyncio
import jack

class Bristol:
    def __init__(self, hardware, midi, screen, loop):
        self.hardware = hardware
        # self.hardware.b1_cb = self.b1_handler
        # self.hardware.b2_cb = self.null_button_handler
        # self.hardware.b3_cb = self.null_button_handler
        # self.hardware.b4_cb = self.null_button_handler


        self.hardware.pot1_cb = self.null_handler
        self.hardware.pot2_cb = self.null_handler
        self.hardware.pot3_cb = self.null_handler
        self.hardware.pot4_cb = self.null_handler
        self.hardware.pot5_cb = self.null_handler
        self.hardware.pot6_cb = self.null_handler
        self.hardware.rot1_cb = self.rot1_handler
        self.hardware.rot2_cb = self.null_handler
        self.hardware.rot3_cb = self.null_handler
        self.hardware.rot4_cb = self.null_handler
        self.hardware.touchx_cb = self.null_handler
        self.hardware.touchy_cb  = self.null_handler


        self.midi = midi
        self.loop = loop
        self.screen = screen
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
        self.client = jack.Client('BristolClient')

        self.current_synth_index = 0
        self.synth_index = self.current_synth_index
        self.current_synth = self.available_synths[self.current_synth_index]
        self.menu_line = [self.available_synths[-1], self.available_synths[self.synth_index], self.available_synths[self.synth_index+1]]

        self.reload = False
        self.running = False
        self.loading = self.screen.get_loading()

    async def start_bristol_emu(self):
        self.hardware.stop()
        self.midi.stop()
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
        self.hardware.start()
        print("Ready to go !")

    async def b1_handler(self):
        self.current_synth_index = self.synth_index
        print(f"Button handler : {self.current_synth_index}")
        self.reload = True

    async def null_button_handler(self):
        pass

    async def null_handler(self, data):
        pass

    async def rot1_handler(self, data):
        if data:
            self.synth_index = self.synth_index + 1 if self.synth_index < len(self.available_synths)-2 else 0
            self.menu_line = [self.available_synths[self.synth_index+1], self.available_synths[self.synth_index], self.available_synths[self.synth_index-1]]
        else:
            self.synth_index = self.synth_index - 1 if self.synth_index > 0 else len(self.available_synths)-2
            self.menu_line = [self.available_synths[self.synth_index-1], self.available_synths[self.synth_index], self.available_synths[self.synth_index+1]]
        self.screen.draw_menu(self.menu_line)

    def stop(self):
        self.running = False

    async def start(self):
        self.running = True
        self.loop.create_task(self.screen.start_gif(self.loading))
        try:
            with self.client:
                await asyncio.sleep(5)
                result = os.popen(f"a2jmidid -e")
                self.screen.stop_gif()
                await asyncio.sleep(2)
                try:
                    await asyncio.wait_for(self.start_bristol_emu(), timeout=10.0)
                except asyncio.TimeoutError:
                    print('timeout!')
                    self.screen.draw_text_box(f"{self.current_synth} is not available ...")
                    await asyncio.sleep(2)
                while self.running:
                    if self.current_synth != self.available_synths[self.current_synth_index] or self.reload:
                        try:
                            await asyncio.wait_for(self.start_bristol_emu(), timeout=10.0)
                        except asyncio.TimeoutError:
                            print('timeout!')
                            self.screen.draw_text_box(f"{self.current_synth} is not available ...")
                            self.current_synth == self.available_synths[self.current_synth_index]
                            await asyncio.sleep(2)
                        self.reload = False
                    await asyncio.sleep(0.1)
                result = os.popen("startBristol -exit &")
        except KeyboardInterrupt:
            self.midi.stop()
            self.hardware.stop()
            self.screen.stop()
            self.loop.close()
            result = os.popen("startBristol -exit &")

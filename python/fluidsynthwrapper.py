import os
import asyncio
import jack
import fluidsynth


class FluidSynthWrapper:
    def __init__(self, hardware, midi, screen, loop):
        self.hardware = hardware
        self.hardware.b2_cb = self.b_handler


        self.hardware.pot1_cb = self.pot1_handler
        self.hardware.pot2_cb = self.pot2_handler
        self.hardware.pot3_cb = self.pot3_handler
        self.hardware.pot4_cb = self.pot4_handler
        self.hardware.pot5_cb = self.pot5_handler
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

        self.preset_num = 0
        self.bank_num = 0

        # Init jack client
        self.client = jack.Client('FluidSynthClient')

        self.reload = False
        self.running = False
        self.loading = self.screen.get_loading()
        self.fs = fluidsynth.Synth(2, 48000, 16)
        self.fs.setting('audio.jack.autoconnect', 1)
        self.fs.setting('midi.autoconnect', 1)
        self.sfid = None

    async def b_handler(self):
        self.reload = True

    async def null_handler(self, data):
        pass

    async def rot_handler(self, data):
        if data:
            self.preset_num += 1
        else:
            self.preset_num -= 1
            if self.preset_num < 0:
                self.preset_num = -self.preset_num
        if self.preset_num > 30:
            self.preset_num = 0
        self.fs.program_select(0, self.sfid, 0, self.preset_num)
        sfont_id, bank, program, name = self.fs.channel_info(0)
        self.screen.draw_text_box(f"Preset \n{name.decode()}")

    async def pot1_handler(self, data):
        self.screen.draw_text_box(f"Volume : {int(data/2)}")
        self.fs.cc(0, 7, int(data/2))

    async def pot2_handler(self, data):
        self.screen.draw_text_box(f"expression : {int(data/2)}")
        self.fs.cc(0, 11, int(data/2))

    async def pot3_handler(self, data):
        self.screen.draw_text_box(f"sustain : {int(data/2)}")
        self.fs.cc(0, 64, int(data/2))

    async def pot4_handler(self, data):
        self.screen.draw_text_box(f"reverb : {int(data/2)}")
        self.fs.cc(0, 91, int(data/2))

    async def pot5_handler(self, data):
        self.screen.draw_text_box(f"chorus : {int(data/2)}")
        self.fs.cc(0, 93, int(data/2))

    def stop(self):
        self.running = False

    async def start(self):
        self.running = True
        self.loop.create_task(self.screen.start_gif(self.loading))
        try:
            with self.client:
                await asyncio.sleep(1)
                result = os.popen(f"a2jmidid -e")
                await asyncio.sleep(1)
                self.screen.draw_text_box(f"FluidSynth")
                self.fs.start(driver="jack", midi_driver="jack")
                print("############# FS started")
                self.sfid = self.fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
                print("############# FS load font")
                self.fs.program_select(0, self.sfid, 0, 0)
                print("############# FS programm select")
                while not self.client.get_all_connections(self.client.get_ports(is_output=True, is_audio=True, name_pattern='fluidsynth')[0]) or \
                    not self.client.get_all_connections(self.client.get_ports(is_output=True, is_audio=True, name_pattern='fluidsynth')[1]):
                    await asyncio.sleep(0.5)
                while not self.client.get_all_connections(self.client.get_ports(is_midi=True, name_pattern='fluidsynth', is_input=True)[0]):
                    self.client.connect(self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)[0],
                                        self.client.get_ports(is_midi=True, name_pattern='fluidsynth', is_input=True)[0])
                    await asyncio.sleep(0.5)
                print("############# FS running")
                sfont_id, bank, program, name = self.fs.channel_info(0)
                self.screen.stop_gif()
                self.screen.draw_text_box(f"Preset \n{name.decode()}")
                self.hardware.start()
                while self.running:
                    await asyncio.sleep(1)
                self.fs.delete()
        except KeyboardInterrupt:
            self.midi.stop()
            self.hardware.stop()
            self.screen.stop()
            self.loop.close()
            self.fs.delete()

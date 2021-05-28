import os
import asyncio
import fluidsynth


class FluidSynthWrapper:
    def __init__(self, hardware, midi, screen, loop, jack_client):
        self.client = jack_client
        self.hardware = hardware
        self.hardware.b2_cb = self.b_handler, None

        # self.hardware.pot1_cb = self.pot1_handler
        # self.hardware.pot2_cb = self.pot2_handler
        # self.hardware.pot3_cb = self.pot3_handler
        # self.hardware.pot4_cb = self.pot4_handler
        # self.hardware.pot5_cb = self.pot5_handler
        self.hardware.rot2_cb = self.rot_handler

        self.midi = midi
        self.loop = loop
        self.screen = screen

        self.preset_num = 0
        self.bank_num = 0

        self.reload = False
        self.running = False
        self.loading = self.screen.get_loading()
        self.fs = fluidsynth.Synth(2, 48000, 16)
        self.fs.setting('audio.jack.autoconnect', 1)
        self.fs.setting('midi.autoconnect', 1)
        self.sfid = None

        self.cc = self.fs.cc

    def b_handler(self):
        self.reload = True

    def rot_handler(self, data):
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

    def stop(self):
        self.running = False
        src = self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)
        dest = self.client.get_ports(is_midi=True, name_pattern='fluidsynth', is_input=True)
        if src and dest:
            self.client.disconnect(src[0], dest[0])
        self.fs.delete()

    async def start(self):
        self.running = True
        try:
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
                try:
                    src = self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)
                    dest = self.client.get_ports(is_midi=True, name_pattern='fluidsynth', is_input=True)
                    if src and dest:
                        self.client.connect(src[0], dest[0])
                except Exception as error:
                    print(error)
                await asyncio.sleep(0.5)
            print("############# FS running")
            sfont_id, bank, program, name = self.fs.channel_info(0)
            # self.screen.stop_gif()
            self.screen.draw_text_box(f"Preset \n{name.decode()}")
        except KeyboardInterrupt:
            self.fs.delete()

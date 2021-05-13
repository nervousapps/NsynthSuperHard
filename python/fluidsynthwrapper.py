import os
import asyncio
import jack
import fluidsynth


class FluidSynthWrapper:
    def __init__(self, hardware, midi, screen, loop):
        self.hardware = hardware
        self.hardware.b1_cb = self.b1_handler
        self.hardware.b2_cb = self.null_handler
        self.hardware.b3_cb = self.null_handler
        self.hardware.b4_cb = self.null_handler


        self.hardware.pot1_cb = self.pot1_handler
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

        self.preset_num = 0
        self.bank_num = 0

        # Init jack client
        self.client = jack.Client('FluidSynthClient')

        self.reload = False
        self.running = False
        self.loading = self.screen.get_loading()
        self.fs = fluidsynth.Synth(gain=2, samplerate=48000, channels=256)
        self.sfid = None

    async def b1_handler(self):
        self.reload = True

    async def null_handler(self, data):
        pass

    async def rot1_handler(self, data):
        self.preset_num += 1
        self.fs.program_select(0, self.sfid, 0, self.preset_num)

    async def pot1_handler(self, data):
        self.screen.draw_text_box(f"Volume : {int(data/2)}")
        self.fs.cc(0, 7, int(data/2))

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
                # result = os.popen(f"fluidsynth -a jack -j -i /usr/share/sounds/sf2/FluidR3_GM.sf2 &")
                self.screen.draw_text_box(f"FluidSynth")
                self.fs.start()
                print("############# FS started")
                self.sfid = self.fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
                print("############# FS load font")
                self.fs.program_select(0, self.sfid, 0, 0)
                print("############# FS programm select")
                while not self.client.get_all_connections(self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)[0]):
                    print(self.client.get_all_connections(self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)[0]))
                    try:
                        self.client.connect(self.client.get_ports(is_midi=True, name_pattern='Arturia', is_output=True)[0],
                                            self.client.get_ports(is_midi=True, name_pattern='FLUID Synth', is_input=True)[0])
                    except Exception as error:
                        print(f"################# {error}")
                    await asyncio.sleep(0.5)
                print("############# FS running")
                while self.running:
                    await asyncio.sleep(1)
                self.fs.delete()
        except KeyboardInterrupt:
            self.midi.stop()
            self.hardware.stop()
            self.screen.stop()
            self.loop.close()
            self.fs.delete()

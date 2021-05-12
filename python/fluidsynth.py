import os
import asyncio
import jack

class FluidSynth:
    def __init__(self, hardware, midi, screen, loop):
        self.hardware = hardware
        self.hardware.b1_cb = self.b1_handler
        self.hardware.b2_cb = self.null_handler
        self.hardware.b3_cb = self.null_handler
        self.hardware.b4_cb = self.null_handler


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

        # Init jack client
        self.client = jack.Client('FluidSynthClient')

        self.reload = False
        self.running = False
        self.loading = self.screen.get_loading()

    async def b1_handler(self):
        self.reload = True

    async def null_handler(self, data):
        pass

    async def rot1_handler(self, data):
        self.reload = True

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
                result = os.popen(f"fluidsynth -a jack -j -n -i /usr/share/sounds/sf2/FluidR3_GM.sf2 EvilWays.mid &")
                self.screen.draw_text_box(f"FluidSynth")
                while self.running:
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.midi.stop()
            self.hardware.stop()
            self.screen.stop()
            self.loop.close()
            result = os.popen("startBristol -exit &")
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

    def connect_jack_ports(self):
        # When entering this with-statement, client.activate() is called.
        # This tells the JACK server that we are ready to roll.
        # Our process() callback will start running now.

        # Connect the ports.  You can't do this before the client is activated,
        # because we can't make connections to clients that aren't running.
        # Note the confusing (but necessary) orientation of the driver backend
        # ports: playback ports are "input" to the backend, and capture ports
        # are "output" from it.
        available_ports = self.client.get_ports()
        if not available_ports:
            raise RuntimeError('No available_ports')
        print(available_ports)
        print(f"Connect {available_ports[2]} to {available_ports[0]}")
        self.client.connect(available_ports[2], available_ports[0])
        self.client.connect(available_ports[3], available_ports[1])

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
        else:
            self.synth_index = self.synth_index - 1 if self.synth_index > 0 else len(self.available_synths)-2
        self.screen.draw_menu(self.available_synths[self.synth_index-1], self.available_synths[self.synth_index], self.available_synths[self.synth_index+1])

    async def main(self):
        try:
            self.screen.draw_text_box("NsynthSuperHard")
            await asyncio.sleep(2)

            for image in self.loading:
                await self.screen.draw_image(image)
                await asyncio.sleep(0.1)

            self.screen.draw_menu(self.available_synths[self.synth_index-1], self.available_synths[self.synth_index], self.available_synths[self.synth_index+1])
            self.hardware.start(self.loop)

            with self.client:
                while True:
                    if self.current_synth != self.available_synths[self.current_synth_index] or self.reload:
                        i = 0
                        self.current_synth = self.available_synths[self.current_synth_index]
                        print(f"Synth name : {self.current_synth}")
                        print("Stopping bristol")
                        result = os.popen("startBristol -exit &")
                        await self.screen.start_gif(self.loading)
                        while all(port.name in ['bristol:out_left', 'bristol:out_right'] for port in self.client.get_ports()):
                            await asyncio.sleep(0.5)
                            if i < len(self.loading)-1:
                                i+=1
                            else:
                                 i=0
                        print("Starting bristol")
                        result = os.popen(f"startBristol -{self.current_synth} -jack -midi alsa &")
                        while all("bristol:bristol input" not in port for port in self.midi.get_output_names()) or all(port.name not in ['bristol:out_left', 'bristol:out_right'] for port in self.client.get_ports()):
                            await self.screen.draw_image(self.loading[i])
                            await asyncio.sleep(0.5)
                            if i < len(self.loading)-1:
                                i+=1
                            else:
                                 i=0
                        print("Bristol started")
                        for i in range(3):
                            try:
                                self.connect_jack_ports()
                            except Exception as error:
                                print(f"Retrying to connect jack ports for {i} time")
                                await asyncio.sleep(1)
                        inport, outport = None, None
                        for port in self.midi.get_output_names():
                            if "Arturia" in port:
                                inport = port
                            if "bristol" in port:
                                outport = port
                        self.midi.start(self.loop, inport, outport)
                        print("All connected")
                        self.screen.draw_text(f"Ready to go !")
                        await asyncio.sleep(1)
                        await self.screen.stop_gif()
                        self.hardware.start(self.loop)
                        self.reload = False
                        print("Ready to go !")
                        self.screen.draw_text(f"Current synth \n {self.current_synth}")
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
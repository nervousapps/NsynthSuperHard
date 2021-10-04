import os
import asyncio
import jack

from hardware import Hardware
from midi_jack import JackInterface
from screen import Screen


class BristolWrapper:
    """
    Wrapper for Bristol synth
    """

    def __init__(self,
                 hardware: Hardware,
                 midi: JackInterface,
                 screen: Screen,
                 loop: asyncio.AbstractEventLoop,
                 jack_client: jack.Client):
        self.client = jack_client
        self.hardware = hardware
        self.hardware.b2_cb = self.b_handler
        self.hardware.rot2_cb = self.rot_handler

        self.midi = midi
        self.loop = loop
        self.screen = screen
        # List of available synths
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

        self.current_synth_index = 0
        self.synth_index = self.current_synth_index
        self.current_synth = self.available_synths[self.current_synth_index]
        self.menu_line = [self.available_synths[-1],
                          self.available_synths[self.synth_index], self.available_synths[self.synth_index+1]]

        self.reload = False
        self.running = False
        self.loading = self.screen.get_loading()

    async def start_bristol_emu(self):
        """
        Start a new Bristol process with the choosen synth
        (according to current_synth_index)
        """
        # Stop all hardware task while starting a synth
        self.hardware.stop()
        # Stop all midi task while starting a synth
        # self.midi.stop()
        print("Stopping bristol")
        _ = os.popen("startBristol -exit &")
        # Wait until Bristol audio port is unvailable (ie Bristol is stopped)
        while self.client.get_ports(is_input=True,
                                    is_audio=True,
                                    name_pattern='bristol'):
            await asyncio.sleep(0.5)
        # Set the current synth to the current index
        self.current_synth = self.available_synths[self.current_synth_index]
        # Start a new Bristol instance with the desired synth
        _ = os.popen(
            f"startBristol -{self.current_synth} -jack -autoconn &")
        # Wait until Bristol audio connections are up and running
        while not self.client.get_all_connections(
            self.client.get_ports(is_input=True,
                                  is_audio=True,
                                  name_pattern='playback')[0]) or \
                not self.client.get_all_connections(
                    self.client.get_ports(is_input=True,
                                          is_audio=True,
                                          name_pattern='playback')[1]):
            await asyncio.sleep(0.5)
        # Wait until midi connections are up and running
        # TODO : the midi device name must be selectable
        while not self.client.get_all_connections(
            self.client.get_ports(is_midi=True,
                                  name_pattern='Arturia',
                                  is_output=True)[0]):
            try:
                # Get the midi device port
                src = self.client.get_ports(
                    is_midi=True, name_pattern='Arturia', is_output=True)
                # Get Bristol device port
                dest = self.client.get_ports(
                    is_midi=True, name_pattern='bristol', is_input=True)
                if src and dest:
                    # Connect Bristol to midi device
                    self.client.connect(src[0], dest[0])
            except Exception as error:
                print(error)
            await asyncio.sleep(0.5)
        # Stop the loading animation
        self.screen.stop_gif()
        self.screen.draw_text(f"Ready to go !")
        await asyncio.sleep(2)
        self.reload = False
        # Draw the menu
        self.screen.draw_menu(self.menu_line)
        # Start the hardware task
        self.hardware.start()
        print("Ready to go !")

    def b_handler(self):
        self.current_synth_index = self.synth_index
        print(f"Button handler : {self.current_synth_index}")
        self.reload = True

    def rot_handler(self, data):
        if data:
            self.synth_index = self.synth_index + \
                1 if self.synth_index < len(self.available_synths)-2 else 0
        else:
            self.synth_index = self.synth_index - \
                1 if self.synth_index > 0 else len(self.available_synths)-2
        self.menu_line = [self.available_synths[self.synth_index+1],
                          self.available_synths[self.synth_index], self.available_synths[self.synth_index-1]]
        self.screen.draw_menu(self.menu_line)

    def stop(self):
        """
        Stop all tasks
        """
        self.running = False

    async def start(self):
        """
        Start Bristol tasks
        """
        self.running = True
        # Show loading screen
        self.loop.create_task(self.screen.start_gif(self.loading))
        try:
            # Start a new Bristol instance
            try:
                await asyncio.wait_for(self.start_bristol_emu(), timeout=60.0)
            except asyncio.TimeoutError:
                print('timeout!')
                self.screen.draw_text_box(
                    f"{self.current_synth} is not available ...")
                await asyncio.sleep(2)
            while self.running:
                if self.current_synth != \
                    self.available_synths[self.current_synth_index] or \
                        self.reload:
                    try:
                        # Start a new Bristol instance
                        await asyncio.wait_for(self.start_bristol_emu(),
                                               timeout=60.0)
                    except asyncio.TimeoutError:
                        print('timeout!')
                        self.screen.draw_text_box(
                            f"{self.current_synth} is not available ...")
                        self.current_synth == self.available_synths[self.current_synth_index]
                        await asyncio.sleep(2)
                    self.reload = False
                await asyncio.sleep(0.1)
            # Get the midi device port
            src = self.client.get_ports(
                is_midi=True, name_pattern='Arturia', is_output=True)
            # Get Bristol device port
            dest = self.client.get_ports(
                is_midi=True, name_pattern='bristol', is_input=True)
            if src and dest:
                # Disconnect Bristol from midi device
                self.client.disconnect(src[0], dest[0])
            # Stop Bristol instance
            _ = os.popen("startBristol -exit &")
        except KeyboardInterrupt:
            # Stop Bristol instance
            _ = os.popen("startBristol -exit &")

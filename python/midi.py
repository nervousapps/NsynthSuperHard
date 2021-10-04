"""
NOT USED
"""
import asyncio
import mido
import serial
import jack


class Midi:
    """
    Handle midi events
    """

    def __init__(self, client: jack.Client):
        self.client = client

    def stop(self):
        """
        Stop scanning midi port
        """
        self.running = False

    def start(self, loop, input, output):
        """
        Start scanning midi port
        """
        self.running = True
        # Create an asyncio task
        loop.create_task(self.midi_over_usb_task(input, output))
        loop.create_task(self.midi_over_uart_task(output))

    async def midi_over_usb_task(self, input, output):
        """
        Stream midi usb input to midi output port
        """
        try:
            # Open the desired intput port
            with mido.open_input(input) as inport:
                # Open desired output port
                with mido.open_output(output) as outport:
                    # Enter in the loop
                    while self.running:
                        try:
                            # Read the input port
                            msg = inport.poll()
                            # Do not handle aftertouch event
                            if msg and "aftertouch" not in msg.type:
                                print(msg)
                                # Follow the message to the output port
                                outport.send(msg)
                            await asyncio.sleep(0.01)
                        except Exception as error:
                            print(f"Midi task : {error}")
                            await asyncio.sleep(1)
        except Exception as error:
            print(f"Midi error : {error}")

    async def midi_over_uart_task(self, output=None):
        """
        Scan for midi event over the uart port (MIDIdin)
        """
        # Midi din is on /dev/ttyAMA0, open teh serial port
        ser = serial.Serial('/dev/ttyAMA0', baudrate=38400)

        message = [0, 0, 0]
        # with mido.open_output(output) as outport:
        while True:
            i = 0
            while i < 3:
                data = ord(ser.read(1))  # read a byte
                if data >> 7 != 0:
                    i = 0      # status byte!   this is the beginning of a midi message!
                message[i] = data
                i += 1
                # program change: don't wait for a
                if i == 2 and message[0] >> 4 == 12:
                    # third byte: it has only 2 bytes
                    message[2] = 0
                    i = 3

            messagetype = message[0] >> 4
            # messagechannel = (message[0] & 15) + 1
            # note = message[1] if len(message) > 1 else None
            # velocity = message[2] if len(message) > 2 else None

            if messagetype == 9:    # Note on
                print('Note on')
            elif messagetype == 8:  # Note off
                print('Note off')
            elif messagetype == 12:  # Program change
                print('Program change')
            # outport.send(mido.Message(messagetype, channel=messagechannel, note=note, velocity=velocity))
            await asyncio.sleep(0.05)

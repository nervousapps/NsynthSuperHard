import asyncio
import mido
import serial


class Midi:
    def __init__(self):
        self.running = True

    def get_output_names(self):
        ports = mido.get_output_names()
        print(ports)
        return ports

    def stop(self):
        self.running = False

    def start(self, loop, input, output):
        self.running = True
        loop.create_task(self.midi_task(input, output))

    async def midi_over_usb_task(self, input, output):
        print("################ In midi task")
        try:
            with mido.open_input(input) as inport:
                with mido.open_output(output) as outport:
                    while self.running:
                        try:
                            msg = inport.poll()
                            if msg and "aftertouch" not in msg.type:
                                print(msg)
                                outport.send(msg)
                            await asyncio.sleep(0.01)
                        except Exception as error:
                            print(f"Midi task : {error}")
                            await asyncio.sleep(1)
        except Exception as error:
            print(f"Midi error : {error}")

    async def midi_over_uart_task(self, output=None):
        ser = serial.Serial('/dev/ttyAMA0', baudrate=38400)

        message = [0, 0, 0]
        # with mido.open_output(output) as outport:
        while True:
            i = 0
            while i < 3:
                data = ord(ser.read(1)) # read a byte
                if data >> 7 != 0:
                    i = 0      # status byte!   this is the beginning of a midi message!
                message[i] = data
                i += 1
                if i == 2 and message[0] >> 4 == 12:  # program change: don't wait for a
                    message[2] = 0                      # third byte: it has only 2 bytes
                    i = 3

            messagetype = message[0] >> 4
            messagechannel = (message[0] & 15) + 1
            note = message[1] if len(message) > 1 else None
            velocity = message[2] if len(message) > 2 else None

            if messagetype == 9:    # Note on
                print('Note on')
            elif messagetype == 8:  # Note off
                print('Note off')
            elif messagetype == 12: # Program change
                print('Program change')
            # outport.send(mido.Message(messagetype, channel=messagechannel, note=note, velocity=velocity))
            await asyncio.sleep(0.05)

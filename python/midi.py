import asyncio
import mido


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

    async def midi_task(self, input, output):
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

"""
Jack interface
"""
import asyncio
import mido
import serial
import jack


class JackInterface:
    """
    Jack interface
    """

    def __init__(self, client: jack.Client):
        self.client = client

    async def wait_for_input_audio_port(self):
        pass

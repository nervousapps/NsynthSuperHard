import asyncio


class Encoders:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.rotary_callback = []
        self.previous_data = []

    async def run(self):
        await self._check_encoders_queue()

    async def _check_encoders_queue(self):
        while True:
            datas = await self.queue.get()
            for i, data in enumerate(datas):
                if self.rotary_callback[i]:
                    if (data[i] == 0 and self.previous_data[i] == 255) or \
                       data[i] > self.previous_data[i]:
                        self.loop.call_soon_threadsafe(
                            self.rot1_cb, True)
                    else:
                        self.loop.call_soon_threadsafe(
                            self.rot1_cb, False)

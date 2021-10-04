import pytest
import asyncio
import concurrent.futures
from nsynth_super_lib import HardwareDriver


def test_hardware_driver_launch():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        drivers = HardwareDriver(loop, pool)

        loop.run_until_complete(drivers.launch_drivers())

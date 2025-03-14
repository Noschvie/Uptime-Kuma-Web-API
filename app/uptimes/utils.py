import time
from uptime_kuma_api import UptimeKumaApi


async def get_uptimes(api: UptimeKumaApi):
    uptimes = api.uptime()
    monitors = api.get_monitors()
    timeout = 0.1
    while len(monitors) > len(uptimes) and timeout < 1:
        time.sleep(0.1)
        uptimes = api.uptime()
        timeout += 0.1
    return uptimes

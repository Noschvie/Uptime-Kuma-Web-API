import time
from uptime_kuma_api import UptimeKumaApi


async def get_avg_pings(api: UptimeKumaApi):
    pings = api.avg_ping()
    monitors = api.get_monitors()
    timeout = 0.1
    while len(monitors) > len(pings) and timeout < 1:
        time.sleep(0.1)
        pings = api.avg_ping()
        timeout += 0.1
    return pings

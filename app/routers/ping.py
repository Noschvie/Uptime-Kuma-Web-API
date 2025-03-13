import time

from fastapi import APIRouter, Depends, HTTPException
from uptime_kuma_api import UptimeKumaApi, UptimeKumaException

from config import logger as logging
from schemas.api import API
from utils.deps import get_current_user

router = APIRouter(redirect_slashes=True)


# Sometimes avg_ping data sends later than get_monitors datas
async def get_avg_pings(api: UptimeKumaApi):
    pings = api.avg_ping()
    monitors = api.get_monitors()
    timeout = 0.1
    while len(monitors) > len(pings) and timeout < 1:
        time.sleep(timeout)
        pings = api.avg_ping()
        timeout += 0.1
    return pings


@router.get("", description="Get AVG Ping")
async def get_avg_ping(cur_user: API = Depends(get_current_user)):
    api: UptimeKumaApi = cur_user['api']
    try:
        return await get_avg_pings(api)
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.get("/{monitor_id}", description="Get Avg Ping By Monitor ID")
async def get_avg_ping_by_monitor_id(monitor_id: int, cur_user: API = Depends(get_current_user)):
    api: UptimeKumaApi = cur_user['api']
    try:
        pings = await get_avg_pings(api)
        return pings[monitor_id] if monitor_id in pings else {"message": "Monitor not found!"}
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

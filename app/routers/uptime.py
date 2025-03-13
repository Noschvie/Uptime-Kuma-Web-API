from fastapi import APIRouter, Depends, HTTPException
from uptime_kuma_api import UptimeKumaApi

from config import logger as logging
from schemas.api import API
from utils.deps import get_current_user
import time

router = APIRouter(redirect_slashes=True)


async def get_uptimes(api: UptimeKumaApi):
    uptimes = api.uptime()
    monitors = api.get_monitors()
    timeout = 0.1
    while len(monitors) > len(uptimes) and timeout < 1:
        time.sleep(timeout)
        uptimes = api.uptime()
        timeout += 0.1
    return uptimes


@router.get("", description="Uptime")
async def get_uptime(visitor: API = Depends(get_current_user)):
    try:
        return await get_uptimes(visitor['api'])
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.get("/{monitor_id}", description="Uptime for a specific monitor")
async def get_monitor_uptime(monitor_id: int, visitor: API = Depends(get_current_user)):
    try:
        uptimes = await get_uptimes(visitor['api'])
        return uptimes[monitor_id] if monitor_id in uptimes else 0
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

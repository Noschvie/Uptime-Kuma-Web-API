from fastapi import APIRouter, Depends, HTTPException

from config import logger as logging
from auth.dependencies import get_jwt_session
from auth.schemas import JWTSession
from .utils import get_uptimes

router = APIRouter(redirect_slashes=True)


@router.get("", description="Uptime")
async def get_uptime(s: JWTSession = Depends(get_jwt_session)):
    try:
        return await get_uptimes(s.api)
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.get("/{monitor_id}", description="Uptime for a specific monitor")
async def get_monitor_uptime(monitor_id: int, s: JWTSession = Depends(get_jwt_session)):
    try:
        uptimes = await get_uptimes(s.api)
        return uptimes[monitor_id] if monitor_id in uptimes else 0
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

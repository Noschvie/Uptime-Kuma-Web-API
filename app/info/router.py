from fastapi import APIRouter, Depends, HTTPException

from config import logger as logging
from auth.schemas import JWTSession
from auth.dependencies import get_jwt_session

router = APIRouter(redirect_slashes=True)


@router.get("", description="Get information about the Uptime Kuma API")
async def get_info(s: JWTSession = Depends(get_jwt_session)):
    try:
        return s.api.info()
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

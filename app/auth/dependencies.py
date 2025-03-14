from fastapi import Depends, HTTPException
from uptime_kuma_api import UptimeKumaApi, UptimeKumaException
import jwt
from pydantic import ValidationError

from config import settings, logger as logging
from .schemas import JWTData, JWTSession
from .security import oauth2_token, ALGORITHM


def decode_jwt(token: str) -> JWTData:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        return JWTData(**payload)
    except (jwt.exceptions.InvalidSignatureError, ValidationError) as e:
        logging.info(f"JWT Decode Error: {e}")
        raise HTTPException(status_code=403, detail="Invalid credentials")
    except jwt.exceptions.ExpiredSignatureError as e:
        logging.info(f"JWT Expired: {e}")
        raise HTTPException(status_code=403, detail="Token expired!")


def create_api_session(token_data: JWTData) -> UptimeKumaApi:
    try:
        api = UptimeKumaApi(settings.KUMA_SERVER, wait_events=settings.KUMA_WAIT_EVENTS)
        api.login_by_token(token_data.sub)
        return api
    except UptimeKumaException as e:
        logging.fatal(f"API Login Error: {e}")
        raise HTTPException(status_code=400, detail={"error": str(e)})


async def get_jwt_session(token: str = Depends(oauth2_token)):
    token_data = decode_jwt(token)

    with create_api_session(token_data) as api:
        yield JWTSession(token=token_data.sub, api=api)

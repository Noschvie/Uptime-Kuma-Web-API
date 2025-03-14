from typing import Optional, Any

from pydantic import BaseModel
from uptime_kuma_api import UptimeKumaApi


class JWToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class JWTData(BaseModel):
    sub: Optional[str] = None


class JWTSession(BaseModel):
    token: str
    api: UptimeKumaApi

    class Config:
        arbitrary_types_allowed = True

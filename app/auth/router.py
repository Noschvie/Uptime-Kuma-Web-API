from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from uptime_kuma_api import UptimeKumaException, UptimeKumaApi

from .schemas import JWToken
from .models import User
from .security import create_access_token
from .security import authenticate
from config import logger as logging, settings

router = APIRouter(redirect_slashes=True)


@router.post("/access-token", response_model=JWToken)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_model = await User.get_or_none(username=form_data.username)
    user = authenticate(user_model, form_data.password)

    if not user:
        logging.info("Incorrect username or password")
        raise HTTPException(400, {"message": "Incorrect username or password"})

    try:
        user.last_visit = datetime.now()
        await user.save(update_fields=["last_visit"])

        with UptimeKumaApi(settings.KUMA_SERVER) as api:
            login_response = api.login(settings.KUMA_USERNAME, settings.KUMA_PASSWORD)

        logging.fatal(f"User {user.username} logged in into {settings.KUMA_SERVER}")

        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
        token = create_access_token(login_response["token"], expires)

        return JWToken(access_token=token)
    except UptimeKumaException as e:
        logging.info(e)
        raise HTTPException(400, {"message": "Incorrect Kuma credentials"})
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(400, str(e))

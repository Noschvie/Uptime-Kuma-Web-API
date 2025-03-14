from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from setup import init
from config import settings as app_settings, logger

import auth
import user
import monitors
import pings
import uptimes
import tags
import cert
import database
import info
import settings
import maintenances
import statuspages

app = FastAPI(title=app_settings.PROJECT_NAME)
app.router.redirect_slashes = True

app.include_router(auth.router, prefix="/login", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(monitors.router, prefix="/monitors", tags=["Monitor"])
app.include_router(pings.router, prefix="/pings", tags=["Ping Average"])
app.include_router(uptimes.router, prefix="/uptimes", tags=["Uptime"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(database.router, prefix="/database", tags=["Database"])
app.include_router(statuspages.router, prefix="/status-pages", tags=["Status Pages"])
app.include_router(maintenances.router, prefix="/maintenances", tags=["Maintenances"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(cert.router, prefix="/cert-info", tags=["Certificates Info"])
app.include_router(info.router, prefix="/info", tags=["Server Information"])


@app.on_event("startup")
async def startup():
    await init(app)
    logger.info("KumaAPI started...")


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")

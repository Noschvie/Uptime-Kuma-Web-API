from fastapi import FastAPI
from tortoise import Tortoise
from auth.security import ensure_admin_exists
import db


async def init(app: FastAPI):
    await db.setup()

    @app.on_event("startup")
    async def startup_event():
        await ensure_admin_exists()

    @app.on_event("shutdown")
    async def shutdown_event():
        await Tortoise.close_connections()

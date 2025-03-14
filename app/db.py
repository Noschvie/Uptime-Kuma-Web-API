import os
from tortoise import Tortoise


async def setup():
    if not os.path.exists("../db"):
        os.makedirs("../db", 777)

    await Tortoise.init(
        db_url="sqlite://../db/db.sqlite3",
        modules={"models": ["auth.models"]},
    )

    await Tortoise.generate_schemas()

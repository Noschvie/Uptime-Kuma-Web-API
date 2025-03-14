from fastapi import APIRouter, Depends, HTTPException

from config import logger as logging
from auth.schemas import JWTSession
from auth.dependencies import get_jwt_session

router = APIRouter(redirect_slashes=True)


@router.get("/size", description="Get database size")
async def get_db_size(s: JWTSession = Depends(get_jwt_session)):
    try:
        resp = s.api.get_database_size()
        return {**resp, "unit": "octet"}
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.post("/shrink", description="Shrink database")
async def shrink_db(s: JWTSession = Depends(get_jwt_session)):
    try:
        details = s.api.shrink_database()
        return {"message": "DB Shrinked", "details": details}
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

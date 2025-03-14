from fastapi import HTTPException


def raise_monitor_not_found():
    raise HTTPException(404, {"message": "Monitor not found!"})

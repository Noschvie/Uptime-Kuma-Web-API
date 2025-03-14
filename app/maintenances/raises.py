from fastapi import HTTPException


def raise_maintenance_not_found():
    raise HTTPException(404, {"message": "Maintenance not found!"})

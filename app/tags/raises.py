from fastapi import HTTPException


def raise_tag_not_found():
    raise HTTPException(404, {"message": "Tag not found!"})

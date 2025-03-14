from typing import Optional
from pydantic import BaseModel


class Tag(BaseModel):
    name: str
    color: str


class TagUpdate(BaseModel):
    name: Optional[str]
    color: Optional[str]

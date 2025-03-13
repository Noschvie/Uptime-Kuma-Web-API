from typing import Any
from pydantic import BaseModel


class API(BaseModel):
    token: str
    api: Any

    def __getitem__(self, item):
        return getattr(self, item)

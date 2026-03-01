from pydantic import BaseModel
from typing import Optional


class RepurposeRequest(BaseModel):
    url: Optional[str] = None
    transcript: Optional[str] = None

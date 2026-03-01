from pydantic import BaseModel
from typing import List


class RepurposeResponse(BaseModel):
    summary: str
    tweet_thread: List[str]
    blog_intro: str

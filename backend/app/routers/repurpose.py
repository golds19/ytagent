import logging
import os
import sys
from threading import Lock

from cachetools import TTLCache
from fastapi import APIRouter, HTTPException

# Ensure backend/ is in sys.path so agents can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.transcriber import transcriber_node
from app.models.request import RepurposeRequest
from app.models.response import RepurposeResponse
from app.services.repurpose import repurpose_transcript

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory cache: up to 128 URLs, each entry expires after 1 hour.
# TTLCache is not thread-safe on its own; Lock guards all reads and writes.
_transcript_cache: TTLCache = TTLCache(maxsize=128, ttl=3600)
_cache_lock = Lock()


@router.post("/repurpose", response_model=RepurposeResponse)
async def repurpose_video(request: RepurposeRequest):
    """
    Repurpose a YouTube video into a summary, tweet thread, and blog intro.
    Accepts either a YouTube URL or a raw transcript string.
    """
    if not request.url and not request.transcript:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'url' (YouTube URL) or 'transcript' (raw text)."
        )

    transcript = request.transcript

    if request.url and not transcript:
        with _cache_lock:
            transcript = _transcript_cache.get(request.url)

        if not transcript:
            logger.info(f"Cache miss — fetching transcript for {request.url}")
            result = transcriber_node({"video_url": request.url})
            if result.get("error"):
                raise HTTPException(
                    status_code=422,
                    detail=f"Failed to fetch transcript: {result['error']}"
                )
            transcript = result["transcript"]
            with _cache_lock:
                _transcript_cache[request.url] = transcript
        else:
            logger.info(f"Cache hit — using cached transcript for {request.url}")

    logger.info(f"Repurposing transcript ({len(transcript)} chars)")
    data = await repurpose_transcript(transcript)

    return RepurposeResponse(
        summary=data["summary"],
        tweet_thread=data["tweet_thread"],
        blog_intro=data["blog_intro"],
    )

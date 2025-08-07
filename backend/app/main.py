from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
import os
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from graph.pipeline import create_pipeline, process_video
import logging
from ..webpage.webpage import WebpageSummarizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except asyncio.TimeoutError:
            return HTTPException(status_code=504, detail="Request timeout")

class VideoRequest(BaseModel):
    youtube_url: str
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional configuration parameters")

class ProcessingResponse(BaseModel):
    summaries: List[Dict[str, Any]]
    insights: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: Optional[str] = None

# Add new request model
class WebpageRequest(BaseModel):
    url: str

# Add new response model    
class WebpageMetadata(BaseModel):
    url: str
    length: Optional[int] = None
    word_count: Optional[int] = None
    timestamp: str

class WebpageSummaryResponse(BaseModel):
    status: str
    summary: str
    metadata: WebpageMetadata
    error: Optional[str] = None

app = FastAPI(
    title="YouTube Video Summarizer API",
    description="API for summarizing YouTube videos with AI-powered content analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add timeout middleware
app.add_middleware(TimeoutMiddleware)

@app.post("/summarize", response_model=ProcessingResponse)
async def summarize_video(request: VideoRequest):
    """
    Summarize a YouTube video and provide insights
    
    Args:
        request: VideoRequest object containing YouTube URL and optional config
        
    Returns:
        ProcessingResponse containing summaries, insights, and metadata
    """
    try:
        logger.info(f"Processing video URL: {request.youtube_url}")
        start_time = time.time()
        
        # Process video through pipeline
        result = process_video(request.youtube_url, request.config)
        
        # Check for errors
        if result.get("error"):
            logger.error(f"Pipeline error: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline processing error: {result['error']}"
            )
            
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = ProcessingResponse(
            summaries=result.get("summaries", []),
            insights=result.get("insights"),
            metadata={
                "url": request.youtube_url,
                "processing_time": processing_time,
                "processed_at": datetime.now().isoformat(),
                "content_type": result.get("content_type"),
                "segmentation_info": result.get("segmentation_info"),
                "config_used": request.config
            },
            error=None
        )
        
        logger.info(f"Successfully processed video in {processing_time:.2f} seconds")
        print(response)
        return response
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        error_detail = str(e)
        if "timeout" in error_detail.lower():
            raise HTTPException(
                status_code=504,
                detail="Processing timeout. The video might be too long."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {error_detail}"
        )

@app.post("/api/webpage/summarize", response_model=WebpageSummaryResponse)
async def summarize_webpage(request: WebpageRequest):
    """
    Summarize content from a webpage URL
    """
    try:
        # Initialize summarizer
        summarizer = WebpageSummarizer()
        
        # Process URL and get response
        result = summarizer.process_url(request.url)
        
        # Return the complete response
        return result
        
    except Exception as e:
        logging.error(f"Error summarizing webpage: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize webpage: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
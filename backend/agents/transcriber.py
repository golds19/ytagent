from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_video_id(url: str) -> str:
    """
    Extracts the video ID from a Youtube URL
    """
    if not url:
        raise ValueError("No URL provided")
        
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL format")
    
def transcriber_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for transcribing YouTube videos.
    Expects 'video_url' in state and returns transcript or error.
    """
    try:
        video_url = state.get("video_url")
        if not video_url:
            raise ValueError("No video URL provided in state")
            
        logger.info(f"Transcribing video: {video_url}")
        video_id = get_video_id(video_url)
        
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join(item['text'] for item in transcript_list)
            
            logger.info(f"Successfully transcribed video {video_id}")
            return {
                "transcript": transcript,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Failed to fetch transcript: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "transcript": None
            }
            
    except ValueError as ve:
        error_msg = str(ve)
        logger.error(f"URL validation error: {error_msg}")
        return {
            "error": error_msg,
            "transcript": None
        }
        
    except Exception as e:
        error_msg = f"Unexpected error in transcriber: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "transcript": None
        }

if __name__ == "__main__":
    # Test the transcriber
    test_url = "https://www.youtube.com/watch?v=eE6yvtKLwvk"
    result = transcriber_node({"video_url": test_url})
    print(result)
from youtube_transcript_api import YouTubeTranscriptApi as ytapi

def get_video_id(url: str) -> str:
    """
    Extracts the video ID from a Youtube URL
    """
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")
    
def transcriber_node(state):
    video_url = state["video_url"]
    video_id = get_video_id(video_url)
    try:
        data = ytapi.get_transcript(video_id, languages=['en'])
        final_transcript = ''
        for val in data:
            for key, value in val.items():
                if key == 'text':
                    final_transcript += value
                else:
                    pass
        process_data = final_transcript.split()
        clean_transcript = ' '.join(process_data)
        return {"transcript": clean_transcript}
    except Exception as e:
        return {"error": f"Transcript not found: {e}"}
    
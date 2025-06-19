from youtube_transcript_api import YouTubeTranscriptApi

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
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        transcript = ' '.join(snippet.text for snippet in fetched_transcript)
        #print(f"fetched transcript: {transcript}")
        return {"transcript": transcript}
    except Exception as e:
        print(e)
        return {"error": f"Transcript not found: {e}"}
    
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=eE6yvtKLwvk"
    id = get_video_id(url)
    res = transcriber_node(url)
    print(id)
    print(res)
    
# youtube-summarizer/app/services/transcript_handler.py

from youtube_transcript_api import YouTubeTranscriptApi
# import yt_dlp
# import whisper
import os

def get_youtube_transcript(video_url):
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        return full_text
    except Exception as e:
        raise RuntimeError("Transcript not available via API.") from e

def download_audio(youtube_url, output_path='audio.mp3'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

def transcribe_audio(file_path='audio.mp3'):
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result['text']

def get_transcript_or_transcribe(youtube_url):
    try:
        return get_youtube_transcript(youtube_url)
    except:
        print("No transcript available — using Whisper to transcribe audio...")
        audio_path = 'audio.mp3'
        download_audio(youtube_url, output_path=audio_path)
        transcript = transcribe_audio(audio_path)
        os.remove(audio_path)
        return transcript

# Usage:
# from app.services.transcript_handler import get_transcript_or_transcribe
# transcript = get_transcript_or_transcribe("https://www.youtube.com/watch?v=...")

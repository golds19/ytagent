from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph.pipeline import build_graph
import warnings

warnings.filterwarnings("ignore")

app = FastAPI()
graph = build_graph()

class VideoRequest(BaseModel):
    youtube_url: str

@app.post("/summarize")
def summarize_video(request: VideoRequest):
    try:
        print(f"Preprocessing URL: {request.youtube_url}")
        output = graph.invoke({"video_url": request.youtube_url})
        print(f"Graph output: {output}")
        return {"summaries": output["summaries"], "insights": output["insights"]}
    except Exception as e:
        print(f"Error details: {str(e)}")  # This will show in server logs
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()  # Full stack trace
        raise HTTPException(status_code=500, detail=str(e))
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
        output = graph.invoke({"video_url": request.youtube_url})
        return {"summaries": output["summaries"], "insights": output["insights"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
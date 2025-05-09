from langgraph.graph import StateGraph
from agents.transcriber import transcriber_node
from agents.segmenter import segmenter_node
from agents.summarizer import summarizer_node
from agents.insights import insight_node
from typing import TypedDict, List
import sys

# create the GraphState
class GraphState(TypedDict):
    video_url: str
    transcript: str
    #segments: List[str]
    summaries: str
    insights: str

# Building the agent graph
builder = StateGraph(GraphState)

builder.add_node("Transcriber", transcriber_node)
#builder.add_node("Segmenter", segmenter_node)
builder.add_node("Summarizer", summarizer_node)
builder.add_node("Insight", insight_node)

# drawing the graph using edges
builder.set_entry_point("Transcriber")
builder.add_edge("Transcriber", "Summarizer")
builder.add_edge("Summarizer", "Insight")

builder.set_entry_point("Transcriber")
#builder.add_edge("Transcriber", "Segmenter")
builder.add_edge("Transcriber", "Summarizer")
builder.add_edge("Summarizer", "Insight")

graph = builder.compile()

# Run the pipeline with a sample video URL
if __name__ == "__main__":
    youtube_url = input("Enter Youtube video URL: ")
    output = graph.invoke({"video_url": youtube_url})

    print("\n--- Summary ---")
    print(output["summaries"])
    print("\n------")
    print("\n=== Final Insights ===")
    print(output["insights"])
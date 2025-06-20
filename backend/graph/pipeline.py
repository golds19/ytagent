from langgraph.graph import StateGraph
from agents.transcriber import transcriber_node
# from agents.segmenter import segmenter_node
from agents.summarizer import summarizer_node
from agents.insights import insight_node
from typing import TypedDict, List


class GraphState(TypedDict):
    video_url: str
    transcript: str
    #segments: List[str]
    summaries: str
    insights: str

# Building the agent graph
def build_graph():
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

    return builder.compile()
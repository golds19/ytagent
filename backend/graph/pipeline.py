from typing import Dict, Any, List, Optional, TypedDict, NotRequired
import logging
from langgraph.graph import StateGraph
from backend.agents.transcriber import transcriber_node
from backend.agents.classifier import classifier_node
from backend.agents.segmenter import segmenter_node
from backend.agents.summarizer import summarizer_node
from backend.agents.insights import insights_node
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineState(TypedDict):
    """Type definition for pipeline state"""
    video_url: str  # Changed from url to video_url to match frontend
    url: NotRequired[str]  # Optional alias for backward compatibility
    config: Dict[str, Any]
    error: Optional[str]
    transcript: Optional[str]
    content_type: Optional[str]
    classification: Optional[str]
    segmentation_info: Optional[Dict[str, Any]]
    needs_segmentation: bool
    segments: Optional[List[Dict[str, Any]]]
    summaries: List[Dict[str, Any]]
    generated_insights: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]

def create_pipeline():
    """
    Create the processing pipeline for video content.
    Flow: Transcriber → Classifier → Segmenter → Summarizer → Insights
    """
    
    # Create workflow graph with state schema
    workflow = StateGraph(PipelineState)

    # Add nodes
    workflow.add_node("transcriber", transcriber_node)
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("segmenter", segmenter_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("generate_insights", insights_node)

    # Define edges
    workflow.add_edge("transcriber", "classifier")
    workflow.add_edge("classifier", "segmenter")
    
    # Conditional edge from segmenter based on whether content needs summarization per segment
    def route_to_summarizer(state: PipelineState) -> str:
        """Route to either segment-wise or full summarization."""
        if state.get("needs_segmentation"):
            logger.info("Content requires segment-wise processing")
            return "segment_summarize"
        else:
            logger.info("Content will be processed as a single unit")
            return "full_summarize"
    
    workflow.add_conditional_edges(
        "segmenter",
        route_to_summarizer,
        {
            "segment_summarize": "summarizer",
            "full_summarize": "summarizer"
        }
    )
    
    workflow.add_edge("summarizer", "generate_insights")

    # Set entry point
    workflow.set_entry_point("transcriber")
    
    # Compile graph
    graph = workflow.compile()
    
    return graph

def process_video(url: str, config: Dict = None) -> Dict:
    """
    Process a video through the pipeline.
    
    Args:
        url: URL of the video to process
        config: Optional configuration parameters
        
    Returns:
        Dict containing processing results and metadata
    """
    try:
        # Initialize pipeline
        pipeline = create_pipeline()
        
        # Prepare initial state
        initial_state: PipelineState = {
            "video_url": url,  # Primary URL field
            "url": url,        # Backward compatibility
            "config": config or {},
            "error": None,
            "transcript": None,
            "content_type": None,
            "classification": None,
            "segmentation_info": None,
            "needs_segmentation": False,
            "segments": None,
            "summaries": [],
            "generated_insights": None,
            "metadata": {
                "started_at": datetime.now().isoformat(),
                "completed_at": None,
                "processing_time": None,
                "video_url": url  # Using consistent key in metadata
            }
        }
        
        # Run pipeline
        logger.info(f"Starting pipeline processing for URL: {url}")
        start_time = datetime.now()
        
        result = pipeline.invoke(initial_state)
        
        # Add completion metadata
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        if isinstance(result, dict):
            result["metadata"].update({
                "completed_at": end_time.isoformat(),
                "processing_time": processing_time
            })
            
            # Rename insights key in final result if needed
            if "generated_insights" in result:
                result["insights"] = result.pop("generated_insights")
        
        logger.info("Pipeline processing completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in pipeline processing: {e}")
        return {
            "error": str(e),
            "video_url": url,  # Consistent key in error response
            "metadata": {
                "error_type": type(e).__name__,
                "error_details": str(e),
                "video_url": url  # Consistent key in metadata
            }
        }
from typing import Dict, Any, List, Optional, TypedDict, NotRequired
import logging
from langgraph.graph import Graph, StateGraph
from backend.agents.transcriber import transcriber_node
from backend.agents.classifier import classifier_node
from backend.agents.segmenter import segmenter_node
from backend.agents.summarizer import summarizer_node
from backend.agents.insights import insights_node
from datetime import datetime
import os
import subprocess
from IPython.display import Image
from IPython import display
from backend.graph.pipeline import create_pipeline, PipelineState

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

def create_pipeline() -> Graph:
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

def create_visualization_graph() -> StateGraph:
    """
    Create the graph for visualization purposes (uncompiled version)
    """
    # Create workflow graph with state schema
    workflow = StateGraph(PipelineState)

    # Add nodes
    workflow.add_node("transcriber", "Transcriber")
    workflow.add_node("classifier", "Classifier")
    workflow.add_node("segmenter", "Segmenter")
    workflow.add_node("summarizer", "Summarizer")
    workflow.add_node("generate_insights", "Generate Insights")

    # Define edges
    workflow.add_edge("transcriber", "classifier")
    workflow.add_edge("classifier", "segmenter")
    workflow.add_conditional_edges(
        "segmenter",
        "route_to_summarizer",
        {
            "segment_summarize": "summarizer",
            "full_summarize": "summarizer"
        }
    )
    workflow.add_edge("summarizer", "generate_insights")

    # Set entry point
    workflow.set_entry_point("transcriber")
    
    return workflow

if __name__ == "__main__":
    # Test video URLs for different scenarios
    test_urls = {
        "short": "https://youtu.be/Z24Td5mtKOs?si=K3qMqntXLqB41aEM",  # Replace with actual short video
        "long": "https://www.youtube.com/watch?v=xyz789",   # Replace with actual long video
        "tutorial": "https://www.youtube.com/watch?v=def456" # Replace with actual tutorial
    }
    
    try:
        # Generate Mermaid diagram
        diagram = """
        graph TD
            START((Start)) --> A[YouTube URL]
            A --> B[Transcriber]
            B --> C[Classifier]
            C --> D[Segmenter]
            D -->|Long Content| E1[Segment-wise Summary]
            D -->|Short Content| E2[Full Summary]
            E1 --> F[Generate Insights]
            E2 --> F
            F --> END((End))
        """
        
        # Save the Mermaid diagram as text
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mmd_filename = f"pipeline_diagram_{timestamp}.mmd"
        with open(mmd_filename, 'w', encoding='utf-8') as f:
            f.write(diagram)
        print(f"\nMermaid diagram saved as: {mmd_filename}")
        
        print("Diagram created and displayed.")
    
    except Exception as e:
        print(f"\nError processing diagram: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test with a sample video
    test_url = test_urls["short"]  # Change to test different scenarios
    print(f"\nTesting pipeline with URL: {test_url}")
    
    try:
        # Add some test configuration
        test_config = {
            "language": "en",
            "max_segments": 5,
            "min_segment_words": 500
        }
        
        # Process the video
        result = process_video(test_url, test_config)
        
        # Display results
        print("\nProcessing Results:")
        print(f"Status: {'Success' if not result.get('error') else 'Failed'}")
        print(f"Processing Time: {result.get('metadata', {}).get('processing_time', 'N/A')} seconds")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        else:
            print(f"\nNumber of Segments: {len(result.get('summaries', []))}")
            print(f"Content Type: {result.get('content_type', 'N/A')}")
            print("\nSummaries:")
            for i, summary in enumerate(result.get('summaries', [])):
                print(f"\nSegment {i+1}:")
                if isinstance(summary, dict):
                    print(summary.get('content', 'No content'))
                else:
                    print(summary)
            
            print("\nInsights:")
            insights = result.get('insights', {})
            if isinstance(insights, dict):
                for key, value in insights.items():
                    print(f"\n{key}:")
                    print(value)
            else:
                print(insights)
                
    except Exception as e:
        print(f"\nTest Failed: {str(e)}")
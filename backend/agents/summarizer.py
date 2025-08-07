from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import time
from openai import RateLimitError
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# loading the environment variables from the .env file
load_dotenv()

# Initialize LLMs
openai_llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini-2024-07-18",
    request_timeout=30
)
ollama_llm = OllamaLLM(
    model="llama3.2:latest",
    temperature=0
)

def get_summary_prompt(transcript: str, video_type: str, is_segment: bool = False, segment_info: Dict = None) -> str:
    """
    Returns appropriate summary prompt based on video type and segment information
    """
    base_prompt = "Please summarize the following"
    if is_segment:
        base_prompt += f" segment (part {segment_info['index'] + 1})"
    base_prompt += " transcript"
    
    type_specific_prompts = {
        "Tutorial/How-To": """
            Create a step-by-step summary of this tutorial:
            - List any prerequisites or requirements
            - Extract clear, numbered steps
            - Highlight important warnings or tips
            - Note the expected outcome
            
            Format the summary with clear sections and bullet points.
            """,
            
        "Educational/Lecture": """
            Create an educational summary of this content:
            - Main concepts and definitions
            - Key learning points
            - Important examples or applications
            - Core takeaways
            
            Format the summary with clear sections and bullet points.
            """,
            
        "Podcast/Discussion": """
            Create a discussion summary:
            - Main topics covered
            - Key arguments or viewpoints
            - Important quotes or statements
            - Major conclusions
            
            Format the summary with clear sections and bullet points.
            """,
            
        "General Content": """
            Create a general summary:
            - Main points and themes
            - Key highlights
            - Notable information
            - Important conclusions
            
            Format the summary with clear sections and bullet points.
            """
    }
    
    prompt = f"{base_prompt}:\n\n{type_specific_prompts.get(video_type, type_specific_prompts['General Content'])}\n\nTranscript:\n{transcript}"
    return prompt

def get_global_summary_prompt(segment_summaries: List[Dict], video_type: str) -> str:
    """
    Creates a prompt for generating a global summary from segment summaries
    """
    summaries_text = "\n\n".join([
        f"Segment {i+1}:\n{summary['content']}"
        for i, summary in enumerate(segment_summaries)
        if 'content' in summary
    ])
    
    prompt = f"""Create a comprehensive global summary of this {video_type} content based on the following segment summaries.
    Focus on:
    - Main themes and key points across all segments
    - Important connections between segments
    - Overall progression of ideas
    - Key takeaways from the entire content
    
    Segment Summaries:
    {summaries_text}
    """
    return prompt

def create_global_summary(segment_summaries: List[Dict], video_type: str) -> Dict:
    """
    Creates a global summary from all segment summaries
    """
    try:
        prompt = get_global_summary_prompt(segment_summaries, video_type)
        
        try:
            logger.info("Generating global summary using OpenAI")
            result = openai_llm.invoke(prompt)
            summary_text = result.content if hasattr(result, 'content') else result
        except Exception as e:
            logger.warning(f"OpenAI error for global summary, falling back to Ollama: {e}")
            result = ollama_llm.invoke(prompt)
            summary_text = result.content if hasattr(result, 'content') else result
        
        return {
            "content": summary_text,
            "metadata": {
                "type": "global_summary",
                "video_type": video_type,
                "created_at": datetime.now().isoformat(),
                "model_used": "openai" if "openai" in str(type(result)) else "ollama",
                "segment_count": len(segment_summaries)
            }
        }
    except Exception as e:
        logger.error(f"Error creating global summary: {e}")
        return {
            "error": str(e),
            "type": "global_summary"
        }

def summarize_segment(text: str, classification: str, segment_info: Dict = None) -> Dict:
    """
    Summarizes content based on video type classification and segment information
    Returns a dictionary with summary and metadata
    """
    try:
        # Log input parameters for debugging
        logger.info(f"Starting summarize_segment with segment_info: {segment_info}")
        logger.info(f"Classification input: {classification}")
        
        # Parse classification JSON with better error handling
        try:
            if not isinstance(classification, str):
                logger.error(f"Classification is not a string: {type(classification)}")
                classification = json.dumps({"type": "General Content"})
                
            class_info = json.loads(classification)
            if not isinstance(class_info, dict):
                logger.error(f"Parsed classification is not a dict: {type(class_info)}")
                class_info = {"type": "General Content"}
                
            video_type = class_info.get("type", "General Content")
            logger.info(f"Successfully parsed classification: {video_type}")
        except json.JSONDecodeError as je:
            logger.error(f"JSON parse error in classification: {je}")
            logger.error(f"Raw classification string: '{classification}'")
            # Fallback to general content
            video_type = "General Content"
        except Exception as e:
            logger.error(f"Unexpected error parsing classification: {e}")
            video_type = "General Content"
        
        # Get type-specific prompt
        is_segment = segment_info is not None
        prompt = get_summary_prompt(text, video_type, is_segment, segment_info)
        
        try:
            # Try OpenAI first
            logger.info(f"Attempting to use OpenAI for {video_type} summarization")
            result = openai_llm.invoke(prompt)
            summary_text = result.content if hasattr(result, 'content') else result
            logger.info("Successfully got OpenAI summary")
        except Exception as e:
            logger.warning(f"OpenAI error, falling back to Ollama: {e}")
            try:
                # Fallback to Ollama
                logger.info(f"Using Ollama for {video_type} summarization")
                result = ollama_llm.invoke(prompt)
                if not result:
                    raise Exception("Empty response from Ollama")
                summary_text = result.content if hasattr(result, 'content') else result
                logger.info("Successfully got Ollama summary")
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                raise Exception(f"Both OpenAI and Ollama failed: {str(e)}")
        
        # Validate summary text
        if not isinstance(summary_text, str):
            logger.error(f"Summary text is not a string: {type(summary_text)}")
            raise Exception("Invalid summary text format")
            
        if not summary_text.strip():
            logger.error("Empty summary text received")
            raise Exception("Empty summary received from model")
        
        # Create summary object with metadata
        summary = {
            "content": summary_text,
            "metadata": {
                "video_type": video_type,
                "created_at": datetime.now().isoformat(),
                "model_used": "openai" if "openai" in str(type(result)) else "ollama",
                "content_length": len(summary_text)
            }
        }
        
        # Add segment information if present
        if segment_info:
            if not isinstance(segment_info, dict):
                logger.warning(f"Invalid segment_info format: {type(segment_info)}")
                segment_info = {
                    "index": 0,
                    "word_count": len(text.split())
                }
            
            summary["metadata"].update({
                "segment_index": segment_info.get("index", 0),
                "word_count": segment_info.get("word_count", len(text.split()))
            })
            
        logger.info(f"Successfully created summary object for segment {segment_info.get('index', 'unknown') if segment_info else 'single'}")
        return summary
        
    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing error in summarize_segment: {je}")
        logger.error(f"Problematic JSON string: '{classification}'")
        # Fallback to general summary
        return summarize_segment(text, '{"type": "General Content"}', segment_info)
    except Exception as e:
        logger.error(f"Error in summarize_segment: {str(e)}")
        raise

def summarizer_node(state: Dict) -> Dict:
    """
    Handles both segmented and non-segmented content summarization.
    For long videos (multiple segments), returns the global summary.
    For short videos (single segment), returns the segment summary.
    """
    try:
        # Log initial state for debugging
        logger.info("Summarizer node starting with state keys: %s", list(state.keys()))
        
        # Check if we have segments or a single transcript
        segments = state.get("segments", [])
        logger.info(f"Received {len(segments) if segments else 0} segments")
        
        # Validate segments structure
        if not segments or not isinstance(segments, list):
            logger.warning(f"Invalid segments format: {type(segments)}")
            # Create a single segment from transcript if available
            transcript = state.get("transcript")
            if transcript and isinstance(transcript, str) and transcript.strip():
                logger.info("Falling back to transcript for single segment")
                segments = [{
                    "content": transcript,
                    "metadata": {
                        "index": 0,
                        "word_count": len(transcript.split()),
                        "created_at": datetime.now().isoformat()
                    }
                }]
            else:
                logger.error(f"No valid content provided. Transcript type: {type(transcript)}, Segments: {segments}")
                return {
                    "error": "No valid content provided for summarization",
                    "summaries": []
                }
        
        # Validate segment content
        valid_segments = []
        for i, segment in enumerate(segments):
            if not isinstance(segment, dict):
                logger.error(f"Invalid segment format at index {i}: {type(segment)}")
                continue
                
            content = segment.get("content", "").strip()
            if not content:
                logger.error(f"Empty content in segment {i}")
                continue
                
            metadata = segment.get("metadata", {})
            if not isinstance(metadata, dict):
                logger.warning(f"Invalid metadata in segment {i}, creating default")
                metadata = {
                    "index": i,
                    "word_count": len(content.split()),
                    "created_at": datetime.now().isoformat()
                }
                
            valid_segments.append({
                "content": content,
                "metadata": metadata
            })
            
            logger.info(f"Segment {i} validated - Length: {len(content)}, Words: {len(content.split())}")
        
        if not valid_segments:
            logger.error("No valid segments after validation")
            return {
                "error": "No valid segments available for summarization",
                "summaries": []
            }
        
        segments = valid_segments
        classification = state.get("classification", '{"type": "General Content"}')
        
        try:
            class_info = json.loads(classification)
            video_type = class_info.get("type", "General Content")
        except json.JSONDecodeError:
            logger.warning("Failed to parse classification, using General Content")
            video_type = "General Content"
            
        logger.info(f"Processing content type: {video_type}")
        
        # Process segments sequentially
        summaries = []
        failed_segments = []
        
        for segment in segments:
            try:
                summary = summarize_segment(
                    segment["content"],
                    classification,
                    segment.get("metadata")
                )
                
                if summary and isinstance(summary, dict) and summary.get("content", "").strip():
                    logger.info(f"Successfully summarized segment {segment.get('metadata', {}).get('index', 'unknown')}")
                    summaries.append(summary)
                else:
                    logger.error(f"Invalid summary format for segment {segment.get('metadata', {}).get('index', 'unknown')}: {summary}")
                    failed_segments.append(segment.get("metadata", {}).get("index", "unknown"))
                    
            except Exception as e:
                logger.error(f"Error summarizing segment {segment.get('metadata', {}).get('index', 'unknown')}: {e}")
                failed_segments.append(segment.get("metadata", {}).get("index", "unknown"))
        
        # Check if we have any valid summaries
        if not summaries:
            logger.error("No valid summaries generated")
            return {
                "error": f"Failed to generate summaries. Failed segments: {failed_segments}",
                "summaries": []
            }
        
        logger.info(f"Generated {len(summaries)} valid summaries")
        
        # Log summary content lengths for debugging
        for i, summary in enumerate(summaries):
            logger.info(f"Summary {i} content length: {len(summary.get('content', ''))}")
        
        # For long videos (multiple segments), return only the global summary
        if len(summaries) > 1:
            logger.info("Generating global summary for multiple segments")
            global_summary = create_global_summary(summaries, video_type)
            
            # Check if global summary was created successfully
            if not global_summary or "error" in global_summary:
                logger.error(f"Failed to create global summary: {global_summary}")
                return {
                    "summaries": summaries,  # Fall back to individual summaries if global summary fails
                    "error": f"Failed to create global summary: {global_summary.get('error', 'Unknown error')}"
                }
            
            # Add additional metadata about the segmentation
            global_summary["metadata"].update({
                "is_long_format": True,
                "segment_count": len(summaries),
                "total_words": sum(s.get("metadata", {}).get("word_count", 0) for s in summaries if "metadata" in s),
                "failed_segments": failed_segments if failed_segments else None
            })
            
            logger.info("Successfully created global summary")
            logger.info(f"Global summary content length: {len(global_summary.get('content', ''))}")
            return {
                "summaries": [global_summary],  # Return global summary as the only summary
                "error": None if not failed_segments else f"Some segments failed: {failed_segments}"
            }
        else:
            # For short videos (single segment), return the segment summary
            logger.info("Returning single segment summary")
            logger.info(f"Single summary content length: {len(summaries[0].get('content', ''))}")
            return {
                "summaries": summaries,
                "error": None if not failed_segments else f"Some segments failed: {failed_segments}"
            }
        
    except Exception as e:
        logger.error(f"Error in summarizer_node: {e}")
        return {
            "error": str(e),
            "summaries": []
        }
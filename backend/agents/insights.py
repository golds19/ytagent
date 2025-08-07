from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import time
from openai import RateLimitError
import logging
import json
from typing import List, Dict, Any
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

def get_insights_prompt(summaries: List[Dict[str, Any]], video_type: str) -> str:
    """
    Returns appropriate insights prompt based on video type and handles multiple summaries
    """
    # Validate and extract summary content
    valid_summaries = []
    for summary in summaries:
        if isinstance(summary, dict) and summary.get('content'):
            valid_summaries.append(summary['content'])
        elif isinstance(summary, str) and summary.strip():
            valid_summaries.append(summary)
    
    if not valid_summaries:
        raise ValueError("No valid summary content found")
    
    # Combine summaries if we have multiple segments
    if len(valid_summaries) > 1:
        combined_summary = "\n\n".join([
            f"Part {i+1}:\n{content}"
            for i, content in enumerate(valid_summaries)
        ])
    else:
        combined_summary = valid_summaries[0]
    
    base_prompt = "Based on the following summary, extract key insights"
    
    type_specific_prompts = {
        "Tutorial/How-To": """
            Extract practical insights from this tutorial:
            - Best practices and tips
            - Common pitfalls to avoid
            - Important considerations
            - Alternative approaches (if applicable)
            - Prerequisites and requirements
            
            Format as bullet points, focusing on actionable insights.
            """,
            
        "Educational/Lecture": """
            Extract educational insights from this content:
            - Key concepts and their relationships
            - Practical applications
            - Important principles
            - Learning connections
            - Areas for further study
            
            Format as bullet points, emphasizing understanding and application.
            """,
            
        "Podcast/Discussion": """
            Extract discussion insights from this content:
            - Main arguments and viewpoints
            - Key disagreements or debates
            - Expert recommendations
            - Notable quotes or statements
            - Further discussion points
            
            Format as bullet points, highlighting different perspectives.
            """,
            
        "General Content": """
            Extract general insights from this content:
            - Key takeaways
            - Important implications
            - Notable points
            - Relevant connections
            - Action items
            
            Format as bullet points for clear understanding.
            """
    }
    
    prompt = f"{base_prompt}:\n\n{type_specific_prompts.get(video_type, type_specific_prompts['General Content'])}\n\nSummary:\n{combined_summary}"
    return prompt

def extract_insights(summaries: List[Dict[str, Any]], classification: str) -> Dict[str, Any]:
    """
    Extracts insights based on video type classification and handles multiple summaries
    Returns a dictionary with insights and metadata
    """
    try:
        # Parse classification JSON
        class_info = json.loads(classification)
        video_type = class_info.get("type", "General Content")
        
        # Get type-specific prompt
        prompt = get_insights_prompt(summaries, video_type)
        
        try:
            # Try OpenAI first
            logger.info(f"Attempting to use OpenAI for {video_type} insight extraction")
            result = openai_llm.invoke(prompt)
            insights_text = result.content if hasattr(result, 'content') else result
        except Exception as e:
            logger.warning(f"OpenAI error, falling back to Ollama: {e}")
            try:
                # Fallback to Ollama
                logger.info(f"Using Ollama for {video_type} insight extraction")
                result = ollama_llm.invoke(prompt)
                if not result:
                    raise Exception("Empty response from Ollama")
                insights_text = result.content if hasattr(result, 'content') else result
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                raise Exception(f"Both OpenAI and Ollama failed: {str(e)}")
                
        # Create insights object with metadata
        insights = {
            "content": insights_text,
            "metadata": {
                "video_type": video_type,
                "created_at": datetime.now().isoformat(),
                "model_used": "openai" if "openai" in str(type(result)) else "ollama",
                "num_segments": len(summaries)
            }
        }
        
        return insights
        
    except json.JSONDecodeError:
        logger.error("Failed to parse classification JSON")
        # Fallback to general insights
        return extract_insights(summaries, '{"type": "General Content"}')
    except Exception as e:
        logger.error(f"Error in extract_insights: {e}")
        raise

def insights_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for generating insights from summaries
    """
    try:
        logger.info("Insights node starting with state keys: %s", list(state.keys()))
        summaries = state.get("summaries", [])
        
        # Log received summaries
        logger.info(f"Received {len(summaries) if summaries else 0} summaries")
        
        # Validate summaries structure and content
        if not summaries or not isinstance(summaries, list):
            logger.error(f"Invalid summaries format: {type(summaries)}")
            return {
                "error": "No valid summaries available for insights generation",
                "generated_insights": {
                    "content": "No insights available due to missing summaries",
                    "metadata": {
                        "error": "Invalid summaries format",
                        "created_at": datetime.now().isoformat()
                    }
                }
            }
        
        # Validate each summary
        valid_summaries = []
        for i, summary in enumerate(summaries):
            if not isinstance(summary, dict):
                logger.error(f"Invalid summary format at index {i}: {type(summary)}")
                continue
                
            content = summary.get("content", "")
            if not isinstance(content, str) or not content.strip():
                logger.error(f"Invalid or empty content in summary {i}")
                continue
                
            metadata = summary.get("metadata", {})
            if not isinstance(metadata, dict):
                logger.warning(f"Invalid metadata in summary {i}, creating default")
                metadata = {
                    "created_at": datetime.now().isoformat()
                }
                summary["metadata"] = metadata
                
            valid_summaries.append(summary)
            logger.info(f"Summary {i} validated - Content length: {len(content)}")
        
        if not valid_summaries:
            logger.error("No valid summaries after validation")
            return {
                "error": "No valid summaries available for insights generation",
                "generated_insights": {
                    "content": "No insights available due to invalid summaries",
                    "metadata": {
                        "error": "No valid summaries after validation",
                        "created_at": datetime.now().isoformat()
                    }
                }
            }
        
        classification = state.get("classification", '{"type": "General Content"}')
        try:
            insights = extract_insights(valid_summaries, classification)
            
            if not insights or not isinstance(insights, dict) or not insights.get("content", "").strip():
                logger.error(f"Invalid insights generated: {insights}")
                return {
                    "error": "Failed to generate valid insights",
                    "generated_insights": {
                        "content": "Failed to generate meaningful insights",
                        "metadata": {
                            "error": "Invalid insights format",
                            "created_at": datetime.now().isoformat()
                        }
                    }
                }
            
            logger.info(f"Successfully generated insights - Content length: {len(insights.get('content', ''))}")
            return {
                "generated_insights": insights,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error in extract_insights: {e}")
            return {
                "error": str(e),
                "generated_insights": {
                    "content": f"Failed to generate insights: {str(e)}",
                    "metadata": {
                        "error": str(e),
                        "created_at": datetime.now().isoformat()
                    }
                }
            }
        
    except Exception as e:
        logger.error(f"Error in insights_node: {e}")
        error_msg = str(e)
        return {
            "error": error_msg,
            "generated_insights": {
                "content": f"Failed to generate insights: {error_msg}",
                "metadata": {
                    "error": error_msg,
                    "created_at": datetime.now().isoformat()
                }
            }
        }
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import logging
import json
from typing import Dict, Optional

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

def validate_classification(raw_output: str) -> Optional[Dict]:
    """
    Validates and formats the classification output.
    Returns None if validation fails.
    """
    try:
        # Try to parse as JSON
        classification = json.loads(raw_output)
        
        # Validate required fields
        if not isinstance(classification, dict):
            logger.error(f"Classification is not a dictionary: {type(classification)}")
            return None
            
        # Ensure required fields exist
        required_fields = ["type", "confidence", "reason"]
        for field in required_fields:
            if field not in classification:
                logger.error(f"Missing required field '{field}' in classification")
                return None
                
        # Validate type field
        valid_types = ["Tutorial/How-To", "Educational/Lecture", "Podcast/Discussion", "General Content"]
        if classification["type"] not in valid_types:
            logger.warning(f"Invalid content type: {classification['type']}, defaulting to General Content")
            classification["type"] = "General Content"
            
        # Validate confidence field
        valid_confidence = ["high", "medium", "low"]
        if classification["confidence"] not in valid_confidence:
            logger.warning(f"Invalid confidence value: {classification['confidence']}, defaulting to medium")
            classification["confidence"] = "medium"
            
        return classification
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse classification JSON: {e}")
        logger.error(f"Raw output: {raw_output}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating classification: {e}")
        return None

def classify_content(transcript: str) -> str:
    """
    Classifies the video type based on transcript content.
    Returns type and specific strategy for summarization and insights.
    """
    prompt = f"""Analyze this transcript and classify it into one of these types:
    1. Tutorial/How-To
    2. Educational/Lecture
    3. Podcast/Discussion
    4. General Content

    Consider these patterns:
    - Tutorial: Contains steps, instructions, demonstrations
    - Educational: Explains concepts, provides examples, teaches topics
    - Podcast: Conversational, multiple speakers, opinion-based
    - General: Other content types, standard narrative

    Return the classification as a JSON string with format:
    {{
        "type": "type_name",
        "confidence": "high/medium/low",
        "reason": "brief explanation"
    }}

    The type_name MUST be exactly one of: "Tutorial/How-To", "Educational/Lecture", "Podcast/Discussion", "General Content"
    The confidence MUST be exactly one of: "high", "medium", "low"

    Transcript:
    {transcript[:2000]}...
    """
    
    try:
        # Try OpenAI first
        logger.info("Attempting to use OpenAI for classification")
        result = openai_llm.invoke(prompt)
        raw_output = result.content if hasattr(result, 'content') else result
        
        # Validate OpenAI output
        classification = validate_classification(raw_output)
        if classification:
            logger.info(f"Successfully classified content as {classification['type']} with {classification['confidence']} confidence")
            return json.dumps(classification)
            
        # If OpenAI output is invalid, try Ollama
        logger.warning("Invalid OpenAI classification output, falling back to Ollama")
        
    except Exception as e:
        logger.warning(f"OpenAI error, falling back to Ollama: {e}")
    
    try:
        # Fallback to Ollama
        logger.info("Using Ollama for classification")
        result = ollama_llm.invoke(prompt)
        if not result:
            raise Exception("Empty response from Ollama")
            
        raw_output = result.content if hasattr(result, 'content') else result
        
        # Validate Ollama output
        classification = validate_classification(raw_output)
        if classification:
            logger.info(f"Successfully classified content as {classification['type']} with {classification['confidence']} confidence")
            return json.dumps(classification)
            
        # If both models fail to provide valid output, return default classification
        logger.error("Both models failed to provide valid classification")
        default_classification = {
            "type": "General Content",
            "confidence": "low",
            "reason": "Failed to get valid classification from models"
        }
        return json.dumps(default_classification)
        
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        # Return default classification on error
        default_classification = {
            "type": "General Content",
            "confidence": "low",
            "reason": f"Classification error: {str(e)}"
        }
        return json.dumps(default_classification)

def classifier_node(state: Dict) -> Dict:
    """
    Node function for the langgraph pipeline.
    Takes transcript and returns classification.
    """
    try:
        if not state.get("transcript"):
            logger.error("No transcript provided to classifier")
            return {
                "error": "No transcript provided", 
                "classification": json.dumps({
                    "type": "General Content",
                    "confidence": "low",
                    "reason": "No transcript provided"
                })
            }
            
        classification = classify_content(state["transcript"])
        logger.info(f"Classifier node returning classification: {classification}")
        return {"classification": classification}
        
    except Exception as e:
        logger.error(f"Error in classifier_node: {e}")
        return {
            "error": str(e), 
            "classification": json.dumps({
                "type": "General Content",
                "confidence": "low",
                "reason": f"Classification error: {str(e)}"
            })
        } 
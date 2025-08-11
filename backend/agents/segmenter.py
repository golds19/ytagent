import logging
from typing import List, Dict
import re
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thresholds for content length
THRESHOLDS = {
    "SHORT": 1500,    # No segmentation needed
    "MEDIUM": 4000,   # Optional segmentation
    "LONG": 4000      # Definitely segment
}

# Target segment sizes
SEGMENT_SIZE = {
    "TARGET": 1000,    # Ideal segment size
    "MIN": 1000,       # Minimum segment size
    "MAX": 1500       # Maximum segment size
}

@dataclass
class Segment:
    """Class to hold segment information"""
    content: str
    index: int
    word_count: int
    metadata: Dict

# Natural break markers
BREAK_MARKERS = {
    'strong': [
        r'\n\n+',                          # Multiple newlines
        r'(?i)chapter\s+\d+',              # Chapter markers
        r'(?i)section\s+\d+',              # Section markers
        r'(?i)part\s+\d+',                 # Part markers
        r'(?i)^\d+\.',                     # Numbered lists
        r'(?i)^step\s+\d+',                # Step markers
    ],
    'medium': [
        r'(?i)next,?\s+',                  # Transition words
        r'(?i)now,?\s+',
        r'(?i)moving on',
        r'(?i)let\'s discuss',
        r'(?i)turning to',
    ],
    'weak': [
        r'(?<=[.!?])\s+',                  # Sentence endings
        r'(?i)but',                        # Contrasting transitions
        r'(?i)however',
        r'(?i)moreover',
        r'(?i)furthermore',
    ]
}

def count_words(text: str) -> int:
    """
    Count words in text, handling various whitespace and punctuation.
    """
    if not text:
        return 0
    # Split on whitespace and filter out empty strings
    words = [word for word in text.split() if word.strip()]
    return len(words)

def find_natural_breaks(text: str) -> List[Dict]:
    """
    Find potential break points in the text with their strengths.
    Returns list of dictionaries with position and strength information.
    """
    breaks = []
    
    # Find all potential break points with their strengths
    for strength, patterns in BREAK_MARKERS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                breaks.append({
                    'position': match.start(),
                    'strength': strength,
                    'text': match.group()
                })
    
    # Sort breaks by position
    breaks.sort(key=lambda x: x['position'])
    return breaks

def create_segment(text: str, index: int) -> Segment:
    """
    Create a segment with metadata.
    """
    word_count = count_words(text)
    
    metadata = {
        'index': index,
        'word_count': word_count,
        'created_at': datetime.now().isoformat()
    }
    
    return Segment(
        content=text,
        index=index,
        word_count=word_count,
        metadata=metadata
    )

def segment_transcript(transcript: str) -> List[Segment]:
    """
    Segment the transcript using natural breaks and maintaining semantic coherence.
    """
    segments = []
    current_position = 0
    segment_index = 0
    
    # Find all potential break points
    breaks = find_natural_breaks(transcript)
    current_segment = ""
    
    while current_position < len(transcript):
        # Find next potential break point that would create a segment within size limits
        suitable_break = None
        
        # Look ahead for breaks
        for break_point in breaks:
            if break_point['position'] <= current_position:
                continue
                
            potential_segment = transcript[current_position:break_point['position']].strip()
            word_count = count_words(potential_segment)
            
            # Check if this break point would create a suitable segment
            if word_count >= SEGMENT_SIZE["MIN"]:
                if word_count <= SEGMENT_SIZE["MAX"]:
                    suitable_break = break_point
                    break
                else:
                    # If segment would be too large, force a break at a sentence boundary
                    sentence_breaks = re.finditer(r'(?<=[.!?])\s+', potential_segment)
                    last_good_break = None
                    
                    for sentence_break in sentence_breaks:
                        sentence_segment = potential_segment[:sentence_break.end()]
                        if count_words(sentence_segment) <= SEGMENT_SIZE["MAX"]:
                            last_good_break = sentence_break
                        else:
                            break
                    
                    if last_good_break:
                        suitable_break = {
                            'position': current_position + last_good_break.end(),
                            'strength': 'weak',
                            'text': last_good_break.group()
                        }
                        break
        
        # If no suitable break found and we're not at the end, force a break
        if not suitable_break and current_position < len(transcript):
            words = transcript[current_position:].split()
            if len(words) <= SEGMENT_SIZE["MAX"]:
                # Just take the rest of the transcript
                current_segment = transcript[current_position:].strip()
            else:
                # Take the maximum allowed words
                current_segment = " ".join(words[:SEGMENT_SIZE["MAX"]]).strip()
                # Find the last sentence break in this segment
                last_period = current_segment.rfind(".")
                if last_period > 0:
                    current_segment = current_segment[:last_period + 1].strip()
            
            if current_segment:
                segment = create_segment(current_segment, segment_index)
                segments.append(segment)
            break
        
        # Create segment up to the break point
        current_segment = transcript[current_position:suitable_break['position']].strip()
        if current_segment:
            segment = create_segment(current_segment, segment_index)
            segments.append(segment)
            segment_index += 1
        
        current_position = suitable_break['position']
    
    return segments

def should_segment(transcript: str) -> Dict:
    """
    Determine if transcript needs segmentation based on word count.
    Returns dict with decision and metadata.
    """
    word_count = count_words(transcript)
    
    if word_count <= THRESHOLDS["SHORT"]:
        category = "SHORT"
        needs_segmentation = False
    elif word_count <= THRESHOLDS["MEDIUM"]:
        category = "MEDIUM"
        needs_segmentation = False  # Could be made configurable
    else:
        category = "LONG"
        needs_segmentation = True
        
    return {
        "word_count": word_count,
        "category": category,
        "needs_segmentation": needs_segmentation,
        "threshold_used": THRESHOLDS[category]
    }

def segmenter_node(state):
    """
    Node function for the langgraph pipeline.
    Checks if segmentation is needed and segments if necessary.
    """
    try:
        transcript = state.get("transcript")
        if not transcript:
            logger.error("No transcript provided to segmenter")
            return {
                "error": "No transcript provided",
                "segmentation_info": None,
                "needs_segmentation": False,
                "segments": None
            }

        # Check if we should segment
        segmentation_info = should_segment(transcript)
        logger.info(f"Segmentation analysis: {segmentation_info}")
        
        if segmentation_info["needs_segmentation"]:
            # Perform segmentation for long content
            segments = segment_transcript(transcript)
            logger.info(f"Created {len(segments)} segments")
            
            # Convert segments to dictionary format for state
            segments_data = [
                {
                    "content": seg.content,
                    "metadata": {
                        "index": seg.index,
                        "word_count": seg.word_count,
                        "created_at": seg.metadata["created_at"]
                    }
                }
                for seg in segments
            ]
            
            return {
                "segmentation_info": segmentation_info,
                "needs_segmentation": True,
                "segments": segments_data
            }
        else:
            # For short content, pass through the original transcript
            return {
                "segmentation_info": segmentation_info,
                "needs_segmentation": False,
                "segments": [{
                    "content": transcript,
                    "metadata": {
                        "index": 0,
                        "word_count": segmentation_info["word_count"],
                        "created_at": datetime.now().isoformat()
                    }
                }]
            }
        
    except Exception as e:
        logger.error(f"Error in segmenter_node: {e}")
        return {
            "error": str(e),
            "segmentation_info": None,
            "needs_segmentation": False,
            "segments": None
        }


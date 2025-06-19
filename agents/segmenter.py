
def segment_transcript(transcript, max_word_count=150):
    """
    Segments the transcript into smaller parts based on the max word count.
    """
    words = transcript.split()
    segments = []
    
    for i in range(0, len(words), max_word_count):
        segment = ' '.join(words[i:i + max_word_count])
        segments.append(segment)
    
    return segments

def segmenter_node(state):
    transcript = state["transcript"]
    segments = segment_transcript(transcript)
    return {"segments": segments}


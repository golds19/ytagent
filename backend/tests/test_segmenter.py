"""
Unit tests for agents/segmenter.py
"""
import pytest

from agents.segmenter import (
    count_words,
    should_segment,
    find_natural_breaks,
    segmenter_node,
    THRESHOLDS,
)


# ---------------------------------------------------------------------------
# count_words
# ---------------------------------------------------------------------------

class TestCountWords:
    def test_empty_string(self):
        assert count_words("") == 0

    def test_none_returns_zero(self):
        assert count_words(None) == 0

    def test_single_word(self):
        assert count_words("hello") == 1

    def test_multiple_words(self):
        assert count_words("one two three four five") == 5

    def test_extra_whitespace_ignored(self):
        assert count_words("  word1   word2  ") == 2


# ---------------------------------------------------------------------------
# should_segment
# ---------------------------------------------------------------------------

class TestShouldSegment:
    def test_short_transcript_no_segmentation(self):
        short_text = " ".join(["word"] * 100)  # 100 words < 1500 threshold
        result = should_segment(short_text)
        assert result["needs_segmentation"] is False
        assert result["category"] == "SHORT"
        assert result["word_count"] == 100

    def test_medium_transcript_no_segmentation(self):
        # Between SHORT (1500) and MEDIUM (4000)
        medium_text = " ".join(["word"] * 2000)
        result = should_segment(medium_text)
        assert result["needs_segmentation"] is False
        assert result["category"] == "MEDIUM"

    def test_long_transcript_needs_segmentation(self):
        long_text = " ".join(["word"] * 5000)  # > 4000 threshold
        result = should_segment(long_text)
        assert result["needs_segmentation"] is True
        assert result["category"] == "LONG"

    def test_result_contains_required_keys(self):
        text = "hello world"
        result = should_segment(text)
        assert "word_count" in result
        assert "category" in result
        assert "needs_segmentation" in result
        assert "threshold_used" in result


# ---------------------------------------------------------------------------
# find_natural_breaks
# ---------------------------------------------------------------------------

class TestFindNaturalBreaks:
    def test_no_breaks_in_plain_text(self):
        text = "This is a simple sentence with no break markers."
        # Sentence ending is a 'weak' break — should still find at least one
        breaks = find_natural_breaks(text)
        assert isinstance(breaks, list)

    def test_chapter_marker_detected(self):
        text = "Intro text. Chapter 1 begins here. More content."
        breaks = find_natural_breaks(text)
        positions = [b["position"] for b in breaks]
        assert len(breaks) > 0
        # The break should be at the 'Chapter' marker
        chapter_pos = text.index("Chapter")
        assert chapter_pos in positions

    def test_breaks_sorted_by_position(self):
        text = "Part 1 intro. Section 2 content. Chapter 3 end."
        breaks = find_natural_breaks(text)
        positions = [b["position"] for b in breaks]
        assert positions == sorted(positions)


# ---------------------------------------------------------------------------
# segmenter_node
# ---------------------------------------------------------------------------

class TestSegmenterNode:
    def test_no_transcript_returns_error(self):
        result = segmenter_node({"transcript": None})
        assert result["error"] is not None
        assert result["needs_segmentation"] is False
        assert result["segments"] is None

    def test_missing_transcript_key_returns_error(self):
        result = segmenter_node({})
        assert result["error"] is not None

    def test_short_transcript_not_segmented(self):
        short = " ".join(["word"] * 50)
        result = segmenter_node({"transcript": short})
        assert result["needs_segmentation"] is False
        assert result["segments"] is not None
        # Short transcript should be a single segment
        assert len(result["segments"]) == 1
        assert result["segments"][0]["content"] == short

    def test_short_transcript_segment_has_metadata(self):
        short = "This is a short transcript."
        result = segmenter_node({"transcript": short})
        seg = result["segments"][0]
        assert "content" in seg
        assert "metadata" in seg
        assert "word_count" in seg["metadata"]

    def test_long_transcript_is_segmented(self):
        # Build a transcript with natural break markers so the segmenter can
        # actually split it into multiple segments. A text of repeated identical
        # words has no break points and produces a single max-size segment.
        chunk = (
            "This is a detailed discussion of the topic at hand. "
            "The speaker explains the concept clearly and provides examples. "
        ) * 30  # ~480 words per chunk
        long = "\n\n".join([chunk] * 10)  # 10 paragraphs separated by double newlines

        result = segmenter_node({"transcript": long})
        assert result["needs_segmentation"] is True
        assert result["segments"] is not None
        assert len(result["segments"]) > 1

    def test_segmentation_info_returned(self):
        short = " ".join(["word"] * 10)
        result = segmenter_node({"transcript": short})
        assert result["segmentation_info"] is not None
        assert "word_count" in result["segmentation_info"]

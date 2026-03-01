"""
Unit tests for agents/transcriber.py
"""
import pytest
from unittest.mock import patch, MagicMock

from agents.transcriber import get_video_id, transcriber_node


# ---------------------------------------------------------------------------
# get_video_id
# ---------------------------------------------------------------------------

class TestGetVideoId:
    def test_standard_watch_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert get_video_id(url) == "dQw4w9WgXcQ"

    def test_watch_url_with_extra_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=PLxxx"
        assert get_video_id(url) == "dQw4w9WgXcQ"

    def test_short_youtu_be_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert get_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url_with_query_params(self):
        url = "https://youtu.be/dQw4w9WgXcQ?t=30"
        assert get_video_id(url) == "dQw4w9WgXcQ"

    def test_empty_url_raises(self):
        with pytest.raises(ValueError, match="No URL provided"):
            get_video_id("")

    def test_none_url_raises(self):
        with pytest.raises(ValueError, match="No URL provided"):
            get_video_id(None)

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError, match="Invalid YouTube URL format"):
            get_video_id("https://vimeo.com/12345")


# ---------------------------------------------------------------------------
# transcriber_node
# ---------------------------------------------------------------------------

FAKE_TRANSCRIPT_LIST = [
    {"text": "Hello world", "start": 0.0, "duration": 1.5},
    {"text": "this is a test", "start": 1.5, "duration": 2.0},
]
EXPECTED_TRANSCRIPT = "Hello world this is a test"


class TestTranscriberNode:
    def test_valid_url_returns_transcript(self):
        with patch(
            "agents.transcriber.YouTubeTranscriptApi.get_transcript",
            return_value=FAKE_TRANSCRIPT_LIST,
        ):
            result = transcriber_node({"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})

        assert result["error"] is None
        assert result["transcript"] == EXPECTED_TRANSCRIPT

    def test_youtu_be_url_returns_transcript(self):
        with patch(
            "agents.transcriber.YouTubeTranscriptApi.get_transcript",
            return_value=FAKE_TRANSCRIPT_LIST,
        ):
            result = transcriber_node({"video_url": "https://youtu.be/dQw4w9WgXcQ"})

        assert result["error"] is None
        assert result["transcript"] == EXPECTED_TRANSCRIPT

    def test_transcript_items_are_joined_with_space(self):
        items = [{"text": "A"}, {"text": "B"}, {"text": "C"}]
        with patch(
            "agents.transcriber.YouTubeTranscriptApi.get_transcript",
            return_value=items,
        ):
            result = transcriber_node({"video_url": "https://www.youtube.com/watch?v=abc123"})

        assert result["transcript"] == "A B C"

    def test_empty_url_returns_error(self):
        result = transcriber_node({"video_url": ""})
        assert result["transcript"] is None
        # get_video_id raises ValueError for empty string; transcriber_node
        # catches it and puts the message in "error"
        assert result["error"] is not None

    def test_missing_video_url_key_returns_error(self):
        result = transcriber_node({})
        assert result["transcript"] is None
        assert result["error"] is not None

    def test_invalid_url_format_returns_error(self):
        result = transcriber_node({"video_url": "https://not-a-youtube-url.com"})
        assert result["transcript"] is None
        assert "Invalid YouTube URL format" in result["error"]

    def test_api_failure_returns_error(self):
        with patch(
            "agents.transcriber.YouTubeTranscriptApi.get_transcript",
            side_effect=Exception("Transcripts are disabled for this video"),
        ):
            result = transcriber_node({"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})

        assert result["transcript"] is None
        assert "Failed to fetch transcript" in result["error"]

"""
Unit tests for agents/classifier.py
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from agents.classifier import validate_classification, classifier_node


# ---------------------------------------------------------------------------
# validate_classification
# ---------------------------------------------------------------------------

class TestValidateClassification:
    def test_valid_json_returns_dict(self):
        raw = json.dumps({
            "type": "Educational/Lecture",
            "confidence": "high",
            "reason": "Contains concept explanations",
        })
        result = validate_classification(raw)
        assert result is not None
        assert result["type"] == "Educational/Lecture"
        assert result["confidence"] == "high"

    def test_all_valid_types_accepted(self):
        valid_types = ["Tutorial/How-To", "Educational/Lecture", "Podcast/Discussion", "General Content"]
        for t in valid_types:
            raw = json.dumps({"type": t, "confidence": "high", "reason": "test"})
            result = validate_classification(raw)
            assert result["type"] == t

    def test_invalid_type_falls_back_to_general(self):
        raw = json.dumps({"type": "Unknown Type", "confidence": "high", "reason": "test"})
        result = validate_classification(raw)
        assert result["type"] == "General Content"

    def test_invalid_confidence_falls_back_to_medium(self):
        raw = json.dumps({"type": "Tutorial/How-To", "confidence": "very-high", "reason": "test"})
        result = validate_classification(raw)
        assert result["confidence"] == "medium"

    def test_malformed_json_returns_none(self):
        result = validate_classification("this is not json {{{")
        assert result is None

    def test_missing_required_field_returns_none(self):
        raw = json.dumps({"type": "Tutorial/How-To", "confidence": "high"})  # missing "reason"
        result = validate_classification(raw)
        assert result is None

    def test_non_dict_json_returns_none(self):
        result = validate_classification(json.dumps(["not", "a", "dict"]))
        assert result is None

    def test_empty_string_returns_none(self):
        result = validate_classification("")
        assert result is None


# ---------------------------------------------------------------------------
# classifier_node
# ---------------------------------------------------------------------------

VALID_CLASSIFICATION_JSON = json.dumps({
    "type": "Educational/Lecture",
    "confidence": "high",
    "reason": "Explains concepts clearly",
})


class TestClassifierNode:
    def test_no_transcript_returns_default_classification(self):
        result = classifier_node({"transcript": None})
        assert "classification" in result
        parsed = json.loads(result["classification"])
        assert parsed["type"] == "General Content"

    def test_missing_transcript_key_returns_default(self):
        result = classifier_node({})
        parsed = json.loads(result["classification"])
        assert parsed["type"] == "General Content"

    def test_valid_transcript_openai_success(self, sample_transcript):
        mock_response = MagicMock()
        mock_response.content = VALID_CLASSIFICATION_JSON
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response

        with patch("agents.classifier.openai_llm", mock_llm):
            result = classifier_node({"transcript": sample_transcript})

        assert "classification" in result
        parsed = json.loads(result["classification"])
        assert parsed["type"] == "Educational/Lecture"

    def test_openai_failure_falls_back_to_gemini(self, sample_transcript):
        mock_gemini_response = MagicMock()
        mock_gemini_response.content = VALID_CLASSIFICATION_JSON

        failing_llm = MagicMock()
        failing_llm.invoke.side_effect = Exception("OpenAI down")

        ok_llm = MagicMock()
        ok_llm.invoke.return_value = mock_gemini_response

        with patch("agents.classifier.openai_llm", failing_llm):
            with patch("agents.classifier.geminiLlm", ok_llm):
                result = classifier_node({"transcript": sample_transcript})

        parsed = json.loads(result["classification"])
        assert parsed["type"] == "Educational/Lecture"

    def test_both_llms_fail_returns_default(self, sample_transcript):
        failing_llm = MagicMock()
        failing_llm.invoke.side_effect = Exception("LLM down")

        with patch("agents.classifier.openai_llm", failing_llm):
            with patch("agents.classifier.geminiLlm", failing_llm):
                result = classifier_node({"transcript": sample_transcript})

        parsed = json.loads(result["classification"])
        assert parsed["type"] == "General Content"
        assert parsed["confidence"] == "low"

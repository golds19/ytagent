"""
Unit tests for app/services/repurpose.py
"""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import HTTPException

from app.services.repurpose import repurpose_transcript


VALID_RESULT = {
    "summary": "A great video about AI.",
    "tweet_thread": ["Tweet 1", "Tweet 2", "Tweet 3", "Tweet 4", "Tweet 5"],
    "blog_intro": "Para 1.\n\nPara 2.\n\nPara 3.",
}
VALID_JSON = json.dumps(VALID_RESULT)


def _make_mock_chain(return_value: str) -> AsyncMock:
    """Return an AsyncMock that mimics a LangChain chain with ainvoke."""
    chain = AsyncMock()
    chain.ainvoke.return_value = return_value
    return chain


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestRepurposeTranscript:
    async def test_returns_parsed_dict_on_success(self, sample_transcript):
        with patch("app.services.repurpose._build_chain", return_value=_make_mock_chain(VALID_JSON)):
            with patch("app.services.repurpose.ChatOpenAI"), \
                 patch("app.services.repurpose.ChatGoogleGenerativeAI"):
                result = await repurpose_transcript(sample_transcript)

        assert result["summary"] == VALID_RESULT["summary"]
        assert result["tweet_thread"] == VALID_RESULT["tweet_thread"]
        assert result["blog_intro"] == VALID_RESULT["blog_intro"]

    async def test_strips_json_markdown_fences(self, sample_transcript):
        fenced = "```json\n" + VALID_JSON + "\n```"
        with patch("app.services.repurpose._build_chain", return_value=_make_mock_chain(fenced)):
            with patch("app.services.repurpose.ChatOpenAI"), \
                 patch("app.services.repurpose.ChatGoogleGenerativeAI"):
                result = await repurpose_transcript(sample_transcript)

        assert "summary" in result

    async def test_strips_plain_markdown_fences(self, sample_transcript):
        fenced = "```\n" + VALID_JSON + "\n```"
        with patch("app.services.repurpose._build_chain", return_value=_make_mock_chain(fenced)):
            with patch("app.services.repurpose.ChatOpenAI"), \
                 patch("app.services.repurpose.ChatGoogleGenerativeAI"):
                result = await repurpose_transcript(sample_transcript)

        assert "summary" in result


# ---------------------------------------------------------------------------
# Fallback behaviour
# ---------------------------------------------------------------------------

    async def test_gemini_fallback_when_openai_fails(self, sample_transcript):
        failing_chain = AsyncMock()
        failing_chain.ainvoke.side_effect = Exception("OpenAI rate limit")

        ok_chain = _make_mock_chain(VALID_JSON)

        with patch("app.services.repurpose._build_chain", side_effect=[failing_chain, ok_chain]):
            with patch("app.services.repurpose.ChatOpenAI"), \
                 patch("app.services.repurpose.ChatGoogleGenerativeAI"):
                result = await repurpose_transcript(sample_transcript)

        assert "summary" in result

    async def test_raises_503_when_all_llms_fail(self, sample_transcript):
        failing_chain = AsyncMock()
        failing_chain.ainvoke.side_effect = Exception("All providers down")

        with patch("app.services.repurpose._build_chain", return_value=failing_chain):
            with patch("app.services.repurpose.ChatOpenAI"), \
                 patch("app.services.repurpose.ChatGoogleGenerativeAI"):
                with pytest.raises(HTTPException) as exc_info:
                    await repurpose_transcript(sample_transcript)

        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Invalid JSON from LLM
# ---------------------------------------------------------------------------

    async def test_raises_422_on_invalid_json(self, sample_transcript):
        with patch("app.services.repurpose._build_chain", return_value=_make_mock_chain("not valid json")):
            with patch("app.services.repurpose.ChatOpenAI"), \
                 patch("app.services.repurpose.ChatGoogleGenerativeAI"):
                with pytest.raises(HTTPException) as exc_info:
                    await repurpose_transcript(sample_transcript)

        assert exc_info.value.status_code == 422
        assert "JSON" in exc_info.value.detail

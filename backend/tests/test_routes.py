"""
Integration tests for FastAPI routes using httpx.AsyncClient.
LLM calls and transcript fetching are mocked — no real API keys needed.
"""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app


VALID_REPURPOSE_DATA = {
    "summary": "A great video about machine learning.",
    "tweet_thread": ["Tweet 1", "Tweet 2", "Tweet 3", "Tweet 4", "Tweet 5"],
    "blog_intro": "Para 1.\n\nPara 2.\n\nPara 3.",
}

FAKE_TRANSCRIPT = "This is a test transcript about machine learning and AI."


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _async_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealthRoute:
    async def test_health_returns_200(self):
        async with _async_client() as client:
            resp = await client.get("/health")
        assert resp.status_code == 200

    async def test_health_returns_status_healthy(self):
        async with _async_client() as client:
            resp = await client.get("/health")
        assert resp.json()["status"] == "healthy"

    async def test_health_returns_timestamp(self):
        async with _async_client() as client:
            resp = await client.get("/health")
        assert "timestamp" in resp.json()


# ---------------------------------------------------------------------------
# POST /repurpose
# ---------------------------------------------------------------------------

class TestRepurposeRoute:
    async def test_repurpose_with_transcript_returns_200(self):
        with patch(
            "app.routers.repurpose.repurpose_transcript",
            new_callable=AsyncMock,
            return_value=VALID_REPURPOSE_DATA,
        ):
            async with _async_client() as client:
                resp = await client.post("/repurpose", json={"transcript": FAKE_TRANSCRIPT})

        assert resp.status_code == 200

    async def test_repurpose_response_has_required_keys(self):
        with patch(
            "app.routers.repurpose.repurpose_transcript",
            new_callable=AsyncMock,
            return_value=VALID_REPURPOSE_DATA,
        ):
            async with _async_client() as client:
                resp = await client.post("/repurpose", json={"transcript": FAKE_TRANSCRIPT})

        body = resp.json()
        assert "summary" in body
        assert "tweet_thread" in body
        assert "blog_intro" in body

    async def test_repurpose_tweet_thread_is_list(self):
        with patch(
            "app.routers.repurpose.repurpose_transcript",
            new_callable=AsyncMock,
            return_value=VALID_REPURPOSE_DATA,
        ):
            async with _async_client() as client:
                resp = await client.post("/repurpose", json={"transcript": FAKE_TRANSCRIPT})

        assert isinstance(resp.json()["tweet_thread"], list)

    async def test_repurpose_with_url_fetches_transcript(self):
        mock_transcriber_result = {"transcript": FAKE_TRANSCRIPT, "error": None}
        with patch("app.routers.repurpose.transcriber_node", return_value=mock_transcriber_result):
            with patch(
                "app.routers.repurpose.repurpose_transcript",
                new_callable=AsyncMock,
                return_value=VALID_REPURPOSE_DATA,
            ):
                async with _async_client() as client:
                    resp = await client.post(
                        "/repurpose",
                        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                    )

        assert resp.status_code == 200

    async def test_repurpose_with_url_that_fails_transcript_returns_422(self):
        mock_transcriber_result = {"transcript": None, "error": "Transcript unavailable"}
        with patch("app.routers.repurpose.transcriber_node", return_value=mock_transcriber_result):
            async with _async_client() as client:
                resp = await client.post(
                    "/repurpose",
                    json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                )

        assert resp.status_code == 422

    async def test_repurpose_with_no_body_returns_400(self):
        async with _async_client() as client:
            resp = await client.post("/repurpose", json={})
        assert resp.status_code == 400

    async def test_repurpose_empty_body_returns_400(self):
        async with _async_client() as client:
            resp = await client.post("/repurpose", json={"url": None, "transcript": None})
        assert resp.status_code == 400

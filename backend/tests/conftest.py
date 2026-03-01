"""
Shared test fixtures and configuration for the ReelifyAI backend test suite.
"""
import os
import sys

# Set fake API keys before any app or agent modules are imported.
# Module-level LLM instantiations (e.g. in agents/classifier.py) need these
# env vars to exist, even though no real API calls are made during tests.
os.environ.setdefault("OPENAI_API_KEY", "sk-fake-openai-key-for-testing")
os.environ.setdefault("GOOGLE_API_KEY", "fake-google-key-for-testing")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:8501")

# Add backend/ to sys.path so agents and app packages resolve correctly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ---------------------------------------------------------------------------
# Shared data constants
# ---------------------------------------------------------------------------

SAMPLE_TRANSCRIPT = (
    "Welcome to this video about artificial intelligence and machine learning. "
    "Today we are going to explore how neural networks learn from data. "
    "First, we will cover the basics of supervised learning, where the model "
    "is trained on labeled examples. Then we will discuss unsupervised learning "
    "techniques such as clustering and dimensionality reduction. "
    "Finally, we will look at reinforcement learning, where an agent learns "
    "by interacting with an environment and receiving rewards or penalties. "
    "By the end of this video you will have a solid foundation in the three "
    "main paradigms of machine learning and be ready to dive deeper into each one."
)

SAMPLE_REPURPOSE_RESULT = {
    "summary": (
        "This video provides a comprehensive introduction to the three main "
        "paradigms of machine learning: supervised, unsupervised, and reinforcement "
        "learning. It explains how neural networks learn from labeled data, how "
        "clustering works without labels, and how agents improve through environmental "
        "feedback. Viewers leave with a solid conceptual foundation ready for deeper study."
    ),
    "tweet_thread": [
        "Machine learning has 3 main paradigms and most beginners only know one. Here is a quick thread: ",
        "1/ Supervised learning trains on labeled data. Think image classifiers and spam filters.",
        "2/ Unsupervised learning finds hidden patterns with no labels. Clustering and PCA live here.",
        "3/ Reinforcement learning teaches agents via rewards and penalties. Chess AI is a famous example.",
        "4/ Start with supervised learning, master the basics, then branch out. Thread concluded.",
    ],
    "blog_intro": (
        "Artificial intelligence is reshaping every industry, but the path to understanding it "
        "begins with machine learning.\n\n"
        "In this article we explore the three foundational paradigms — supervised, unsupervised, "
        "and reinforcement learning — and explain when each approach is the right tool for the job.\n\n"
        "Whether you are a complete beginner or an engineer looking to level up, this guide will "
        "give you the mental models you need to navigate the rapidly evolving AI landscape."
    ),
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_transcript_cache():
    """Clear the router-level transcript TTLCache before each test.

    The cache is a module-level object that persists across tests within the
    same process. Without this fixture a URL cached by one test would produce
    a spurious cache-hit in the next test, breaking error-path assertions.
    """
    from app.routers.repurpose import _transcript_cache
    _transcript_cache.clear()
    yield
    _transcript_cache.clear()


@pytest.fixture
def sample_transcript() -> str:
    return SAMPLE_TRANSCRIPT


@pytest.fixture
def sample_repurpose_result() -> dict:
    return SAMPLE_REPURPOSE_RESULT

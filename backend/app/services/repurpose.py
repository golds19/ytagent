import json
import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

REPURPOSE_SYSTEM_PROMPT = """
You are an expert content repurposing strategist for digital creators.
Given a YouTube video transcript, your job is to extract maximum value
and transform it into multiple content formats.

Respond ONLY with valid JSON. No preamble. No markdown code fences. No explanation.
The JSON must have exactly these keys:

{{
  "summary": "A 3-sentence paragraph capturing the core message, main insight, and key takeaway.",
  "tweet_thread": [
    "Tweet 1: Hook — grab attention, state the big idea (≤280 chars)",
    "Tweet 2: Key point 1 with context (≤280 chars)",
    "Tweet 3: Key point 2 with context (≤280 chars)",
    "Tweet 4: Key point 3 or surprising insight (≤280 chars)",
    "Tweet 5: Actionable takeaway or call to action (≤280 chars)"
  ],
  "blog_intro": "Three paragraphs. Para 1: Hook the reader. Para 2: Context and why it matters. Para 3: Preview what the article will cover."
}}
"""

REPURPOSE_USER_TEMPLATE = """
Here is the video transcript:

{transcript}

Generate the content package now.
"""


def _build_chain(llm):
    prompt = ChatPromptTemplate.from_messages([
        ("system", REPURPOSE_SYSTEM_PROMPT),
        ("user", REPURPOSE_USER_TEMPLATE),
    ])
    return prompt | llm | StrOutputParser()


async def repurpose_transcript(transcript: str) -> dict:
    openai_llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=2000,
    )
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
        max_output_tokens=2000,
    )

    raw = None
    for llm, name in [(openai_llm, "OpenAI"), (gemini_llm, "Gemini")]:
        try:
            chain = _build_chain(llm)
            raw = await chain.ainvoke({"transcript": transcript})
            logger.info(f"Repurpose chain completed via {name}")
            break
        except Exception as e:
            logger.warning(f"{name} chain failed: {e}. Trying next LLM.")

    if raw is None:
        raise HTTPException(status_code=503, detail="All LLM providers failed. Please try again later.")

    # Strip markdown fences if model adds them despite instructions
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"LLM returned non-JSON output: {raw[:200]}")
        raise HTTPException(
            status_code=422,
            detail=f"LLM output could not be parsed as JSON: {str(e)}"
        )

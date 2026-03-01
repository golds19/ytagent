# ReelifyAI — Project Evaluation & Upgrade Plan

## Strengths

**Architecture:**
- Clean separation of concerns: routers → services → agents
- Sophisticated multi-agent LangGraph pipeline (Transcriber → Classifier → Segmenter → Summarizer → Insights)
- Dual LLM fallback (OpenAI gpt-4o-mini → Gemini 2.5 Flash) on every agent
- Pydantic models for all request/response shapes + TypedDict for pipeline state
- `start.sh` is excellent — health check polling, signal trapping, colored output

**Product:**
- `/repurpose` is clean, focused, and delivers real value
- Landing page has professional dark purple design
- 3-tab output (Summary / Tweet Thread / Blog Intro) is scannable
- Tweet character count warnings are a thoughtful UX detail

**Code Quality:**
- Type hints used throughout
- Logging in all agents (not just print statements)
- Error recovery at each agent stage
- Well-structured prompt templates

---

## Weaknesses

### Critical (Would fail a code review)

| Issue | File | Impact |
|-------|------|--------|
| Live API keys in `.env` committed to git | `.env`, `.gitignore` | Security breach — rotate keys immediately |
| No tests | Entire codebase | Unacceptable for any professional project |
| `requirements.txt` incomplete | `backend/requirements.txt` | Missing `httpx`, `tenacity`, `pytest` |
| CORS allows all origins (`"*"`) | `backend/app/main.py:68` | Production security risk |
| No input validation on frontend | `frontend/pages/youtube_summarizer.py` | Accepts garbage URLs, sends to API |

### High (Portfolio red flags)

| Issue | File | Impact |
|-------|------|--------|
| LLM instantiated on every `/repurpose` call | `backend/app/services/repurpose.py` | Wasteful, slow, not production-grade |
| Agents are synchronous — no async | `backend/agents/*.py` | Blocks event loop; can't parallelize |
| No caching (same URL re-fetched every time) | All services | Expensive and slow |
| Disabled webpage summarizer left in codebase | `backend/app/main.py`, `backend/webpage/` | Signals abandoned work |
| `pdf_utils.py` not wired to anything | `frontend/utils/pdf_utils.py` | Dead code |
| docker-compose missing health checks + restart policies | `docker-compose.yml` | Services crash and don't recover |
| No retry logic on frontend | `frontend/pages/youtube_summarizer.py` | Bad UX — user must re-enter URL on failure |
| No public deployment | — | Portfolio project with no live URL is weak |

### Medium (Polish gaps)

- No structured logging or request IDs
- Model names and thresholds hardcoded — not configurable
- `sys.path.append()` in agents (fragile import resolution)
- No rate limiting on any endpoint
- Mobile layout untested
- README missing live demo link and architecture diagram

---

## Upgrade Plan

### Phase 1 — Fix Critical Issues ✅ (implementing now)

- [ ] Rotate all exposed API keys (OpenAI, Google, LangSmith, Firecrawl) — **user action required**
- [x] Fix `.gitignore` — ensure `.env` is excluded; create `.env.example`
- [x] Fix `backend/requirements.txt` — add `httpx`, `tenacity`, `pytest`, `pytest-asyncio`
- [x] Restrict CORS — `ALLOWED_ORIGINS` env var in `config.py`; default to localhost in dev

### Phase 2 — Add Tests

- [ ] `backend/tests/conftest.py` — pytest setup, shared fixtures
- [ ] `backend/tests/test_transcriber.py` — valid URL, invalid URL, no captions
- [ ] `backend/tests/test_classifier.py` — valid JSON output, malformed JSON fallback
- [ ] `backend/tests/test_segmenter.py` — short/medium/long transcript thresholds
- [ ] `backend/tests/test_repurpose_service.py` — mock chain, JSON parsing + fallback
- [ ] `backend/tests/test_routes.py` — integration tests via `httpx.AsyncClient`

### Phase 3 — Performance & Robustness

- [ ] Cache LLM instances at module level (`backend/app/services/repurpose.py`)
- [ ] Add in-memory transcript cache — `cachetools.TTLCache` keyed by URL (TTL: 1h)
- [ ] Add retry with backoff — `tenacity` on LLM calls in all agents
- [ ] Add token length guard — truncate transcript if > 100k chars
- [ ] Docker health checks + `restart: unless-stopped` in `docker-compose.yml`

### Phase 4 — Frontend Polish

- [ ] YouTube URL validation — client-side regex before calling API
- [ ] Retry button — show "Try Again" on failure without re-entering URL
- [ ] Handle edge cases — empty tweet array, null summary, malformed blog intro
- [ ] Individual copy buttons on each tweet card

### Phase 5 — Portfolio Signal

- [ ] Public deployment — Railway (backend) + Streamlit Community Cloud (frontend)
- [ ] Live demo URL at top of README
- [ ] Demo GIF in README showing the full flow
- [ ] LangSmith tracing enabled
- [ ] Version + uptime in `/health` response
- [ ] Delete dead code: `backend/webpage/`, `frontend/utils/pdf_utils.py`, `frontend/webpage_summarizer.py`
- [ ] Architecture diagram in README

---

## Files Modified in Phase 1

| File | Change |
|------|--------|
| `.gitignore` | Verified `.env` excluded |
| `.env.example` | New — placeholder keys |
| `backend/requirements.txt` | Added httpx, tenacity, pytest, pytest-asyncio |
| `backend/app/config.py` | Added `allowed_origins` setting |
| `backend/app/main.py` | CORS now reads from `settings.allowed_origins` |

## Files to Delete (Phase 5)

- `backend/webpage/` — disabled feature, entire directory
- `frontend/utils/pdf_utils.py` — dead code, unwired
- `frontend/webpage_summarizer.py` — root-level duplicate

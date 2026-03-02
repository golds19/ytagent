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

---

# ReelifyAI — Ship & Launch Plan

## Context

The product is feature-complete (Phases 1–4 done). The CI/CD pipeline already builds and
pushes Docker images to Docker Hub on every push to `main`. What's missing is a live
hosting environment for both services and a public URL to hand to users.

**Goal:** Get a shareable public URL working end-to-end, then post it where the target
audience lives.

---

## Current State

| What exists | Status |
|---|---|
| GitHub Actions → Docker Hub CI/CD | ✅ Working |
| Docker images (`benphil/yt-summarizer-*`) | ✅ On Docker Hub |
| `docker-compose.yml` (uses pre-built images) | ✅ Works locally |
| Backend Dockerfile uses `--reload` | ❌ Dev-only flag, remove for prod |
| CORS locked to localhost | ❌ Must add prod frontend URL |
| Hosting platform | ❌ None configured |

---

## Recommended Deployment Stack

| Service | Platform | Why |
|---|---|---|
| **Backend (FastAPI)** | Railway | Supports Docker Hub images natively, $5/mo free credit, doesn't spin down (unlike Render free tier) |
| **Frontend (Streamlit)** | Streamlit Community Cloud | Purpose-built for Streamlit, completely free, deploys from GitHub in 2 minutes |

---

## Implementation Steps

### Step 1 — Fix backend Dockerfile for production

**File:** `backend/Dockerfile`

Remove the `--reload` flag from the `CMD`:

```dockerfile
# Before (dev-only)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# After (production)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Commit and push to `main` → CI/CD rebuilds the Docker image automatically.

---

### Step 2 — Deploy backend to Railway

1. Go to [railway.app](https://railway.app) → **New Project → Deploy from Docker image**
2. Image: `benphil/yt-summarizer-backend:latest`
3. Set environment variables in Railway dashboard:
   ```
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=AIza...
   ALLOWED_ORIGINS=http://localhost:8501   ← update in Step 4
   ```
4. Railway generates a public URL, e.g.:
   `https://reelifyai-backend.up.railway.app`

---

### Step 3 — Deploy frontend to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Connect GitHub repo → select `frontend/app.py` as the entry point
3. In **Secrets** (`.streamlit/secrets.toml` equivalent):
   ```toml
   BACKEND_URL = "https://reelifyai-backend.up.railway.app"
   ```
4. Streamlit generates a public URL, e.g.:
   `https://reelifyai.streamlit.app`

---

### Step 4 — Update CORS on Railway

Back in the Railway dashboard, update the environment variable:
```
ALLOWED_ORIGINS=https://reelifyai.streamlit.app
```

Railway redeploys automatically. No code change needed — `config.py` already
parses `ALLOWED_ORIGINS` as a comma-separated list via `allowed_origins_list`.

---

### Step 5 — Verify end-to-end

1. Open the Streamlit URL
2. Paste `https://youtu.be/dQw4w9WgXcQ` → should return content package
3. Test the error path: paste `not a url` → error card shown, no API call fired
4. Download PDF → verify it generates

---

### Step 6 — Future: auto-deploy on push

To make Railway re-pull the latest Docker Hub image on every CI/CD build, add a
Railway deploy webhook to `.github/workflows/deploy.yml`:

```yaml
- name: Trigger Railway redeploy
  run: |
    curl -X POST "${{ secrets.RAILWAY_DEPLOY_WEBHOOK }}"
```

Add `RAILWAY_DEPLOY_WEBHOOK` as a GitHub secret (found in Railway service settings).

---

## Getting Users

Post these **in order** — Reddit first (free, fast, targeted), Product Hunt later
(requires prep but higher ceiling).

### Day 1 — Reddit (post both on the same day, different times)

**r/SideProject** (post at ~10am EST):
> "I had a half-finished YouTube summarizer sitting in my repo for months. Spent 2 days
> turning it into a full content repurposing engine — paste a URL, get a tweet thread,
> summary, and blog intro instantly. No account needed. Live link in comments, would love
> brutal feedback."

**r/contentcreation** (post at ~6pm EST):
> "Tired of spending 2 hours repurposing each video? I built a free tool — paste your
> YouTube link and get a tweet thread + blog post in 10 seconds. No account needed.
> Try it and tell me what's missing."

### Day 2 — Twitter/X & LinkedIn

Tweet the before/after: "2 days, 1 repo, from dead side project → live product"
with a short screen recording (Loom or GIF) of the 3-tab output rendering.

### Day 3 — Hacker News (Show HN)

```
Show HN: ReelifyAI – paste a YouTube URL, get tweet thread + summary + blog intro
```

HN rewards technical depth — mention the LangGraph pipeline, LLM fallback, and
the 61-test suite in the comments if asked.

### Later — Product Hunt

Requires a scheduled launch, a maker profile, and a gallery of screenshots.
Do this after you have at least 10–20 real users and some testimonials to show.

---

## Files Modified

| File | Change |
|---|---|
| `backend/Dockerfile` | Remove `--reload` from CMD |

All other changes are configuration in Railway and Streamlit Cloud dashboards.

---

## Verification Checklist

- [ ] `https://<railway-url>/health` returns `{"status":"healthy",...}`
- [ ] `https://<streamlit-url>` loads the landing page
- [ ] Paste a YouTube URL → content package renders in all 3 tabs
- [ ] PDF download works
- [ ] Invalid URL → error card, no spinner
- [ ] CORS error is absent in browser console

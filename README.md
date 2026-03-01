# ReelifyAI

Paste a YouTube URL — get a tweet thread, summary, and blog intro in seconds.

## What it does

- **Summary** — 3-sentence paragraph capturing the core message and key takeaway
- **Tweet Thread** — 5-tweet thread ready to post, hook through call-to-action
- **Blog Intro** — 3-paragraph opener: hook, context, and article preview

## Tech Stack

FastAPI · LangChain · OpenAI GPT-4o-mini · Gemini 2.5 Flash (fallback) · LangGraph · Streamlit · Docker

## Requirements

- Python 3.10+
- `OPENAI_API_KEY` (required)
- `GOOGLE_API_KEY` (optional — Gemini fallback)

## Running Locally

### Option A — Launch script (recommended)

Starts the backend, waits for it to be healthy, then starts the frontend.

```bash
bash start.sh
```

- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- Backend logs: `backend.log`

Press `Ctrl+C` to stop both services.

### Option B — Manual (two terminals)

**Terminal 1 — Backend:**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

## Running with Docker

Uses prebuilt images from Docker Hub — no local build required.

1. Create a `.env` file (see [Environment Variables](#environment-variables) below).

2. Start the stack:

```bash
docker-compose up
```

3. Open http://localhost:8501.

To stop:

```bash
docker-compose down
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...      # optional — enables Gemini fallback
BACKEND_URL=http://localhost:8000
RUNNING_IN_DOCKER=false
```

When running with Docker Compose, `RUNNING_IN_DOCKER` is set automatically. `BACKEND_URL` inside the container resolves via the service name (`http://backend:8000`).

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/repurpose` | YouTube URL → `{summary, tweet_thread, blog_intro}` |
| `POST` | `/summarize` | YouTube URL → full pipeline (segments + insights) |
| `GET` | `/health` | Health check |

**`POST /repurpose` request body:**

```json
{ "url": "https://www.youtube.com/watch?v=..." }
```

**Response:**

```json
{
  "summary": "...",
  "tweet_thread": ["tweet 1", "tweet 2", "tweet 3", "tweet 4", "tweet 5"],
  "blog_intro": "..."
}
```

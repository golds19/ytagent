#!/usr/bin/env bash
# ReelifyAI — Development launcher
# Starts the FastAPI backend, waits until it is healthy, then starts the Streamlit frontend.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

BACKEND_PORT=8000
FRONTEND_PORT=8501
HEALTH_URL="http://localhost:${BACKEND_PORT}/health"
MAX_WAIT=60   # seconds to wait for backend before giving up

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

log()  { echo -e "${CYAN}[reelify]${RESET} $*"; }
ok()   { echo -e "${GREEN}[reelify]${RESET} $*"; }
warn() { echo -e "${YELLOW}[reelify]${RESET} $*"; }
err()  { echo -e "${RED}[reelify]${RESET} $*"; }

cleanup() {
    echo ""
    warn "Shutting down..."
    if [[ -n "${BACKEND_PID:-}" ]]; then
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
    ok "Done. Goodbye."
}
trap cleanup INT TERM EXIT

# ── Backend ───────────────────────────────────────────────────────────────────
log "Starting backend on port ${BACKEND_PORT}..."

cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload \
    > "$SCRIPT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

log "Backend PID: ${BACKEND_PID}  (logs → backend.log)"

# ── Wait for backend health ───────────────────────────────────────────────────
log "Waiting for backend to be ready..."
elapsed=0

while true; do
    # Check if the process is still alive
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        err "Backend process exited unexpectedly. Check backend.log for details."
        exit 1
    fi

    # Try the health endpoint
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        ok "Backend is ready! (${elapsed}s)"
        break
    fi

    if [[ "$elapsed" -ge "$MAX_WAIT" ]]; then
        err "Backend did not become healthy within ${MAX_WAIT}s. Check backend.log."
        exit 1
    fi

    sleep 1
    elapsed=$((elapsed + 1))
    printf "\r${CYAN}[reelify]${RESET} Waiting... ${elapsed}s"
done

echo ""   # newline after the progress dots

# ── Frontend ──────────────────────────────────────────────────────────────────
log "Starting frontend on port ${FRONTEND_PORT}..."

cd "$FRONTEND_DIR"
streamlit run app.py \
    --server.port "$FRONTEND_PORT" \
    --server.address 0.0.0.0 \
    --server.headless true

# When streamlit exits the script falls through to the EXIT trap → cleanup

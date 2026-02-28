#!/usr/bin/env bash
set -euo pipefail

SEED="${1:-20260225}"
SPEED="${2:-30}"
RESET="${3:---reset}"
API="http://localhost:8000"
FRONTEND="http://localhost:3000"

echo "============================================"
echo " CourtOps Municipal Shift Simulation"
echo " Corpus Christi Public Data Mode"
echo "============================================"
echo "Seed:  $SEED"
echo "Speed: ${SPEED}x"
echo ""

# --- Step 1: Ensure Docker containers ---
echo "[1/6] Starting PostgreSQL + Redis..."
if command -v docker &>/dev/null; then
    sudo dockerd &>/tmp/dockerd.log 2>&1 &
    sleep 2
    sudo docker start courtops-db courtops-redis 2>/dev/null || \
        (sudo docker run -d --name courtops-db -e POSTGRES_USER=courtops -e POSTGRES_PASSWORD=courtops_password -e POSTGRES_DB=courtops_db -p 5432:5432 postgres:15 2>/dev/null && \
         sudo docker run -d --name courtops-redis -p 6379:6379 redis:7 2>/dev/null) || true
    sleep 3
else
    echo "Docker not found - assuming PostgreSQL and Redis are already running."
fi

# --- Step 2: Start backend ---
echo "[2/6] Starting backend..."
cd "$(dirname "$0")/../backend"
if [ -d venv ]; then
    source venv/bin/activate
fi
POSTGRES_HOST=localhost REDIS_URL=redis://localhost:6379/0 \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &>/tmp/backend_demo.log &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 5

# Verify backend is up
if ! curl -sf "$API/health" >/dev/null; then
    echo "ERROR: Backend failed to start. Check /tmp/backend_demo.log"
    exit 1
fi
echo "Backend is healthy."

# --- Step 3: Seed database ---
echo "[3/6] Seeding database (profile=corpus_christi, seed=$SEED)..."
curl -sf -X POST "$API/admin/seed?profile=corpus_christi&scenario=municipal_shift&seed=$SEED&reset=true" | python3 -m json.tool
echo "Seed complete."

# --- Step 4: Start frontend ---
echo "[4/6] Starting frontend..."
cd "$(dirname "$0")/../frontend"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 20 2>/dev/null || true
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev &>/tmp/frontend_demo.log &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
sleep 8

# --- Step 5: Start simulation ---
echo "[5/6] Starting simulation (speed=${SPEED}x)..."
curl -sf -X POST "$API/admin/sim/start?speed=$SPEED" | python3 -m json.tool

# --- Step 6: Print recording URL ---
echo ""
echo "============================================"
echo " SIMULATION RUNNING"
echo "============================================"
echo ""
echo " Ops Console:  $FRONTEND/ops"
echo " Tour Mode:    $FRONTEND/ops?tour=1"
echo " API Docs:     $API/docs"
echo " SSE Stream:   $API/ops/stream"
echo ""
echo " Backend PID:  $BACKEND_PID"
echo " Frontend PID: $FRONTEND_PID"
echo ""
echo " To stop: ./scripts/stop_demo.sh"
echo "============================================"

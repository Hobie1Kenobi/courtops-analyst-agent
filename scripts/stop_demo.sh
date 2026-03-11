#!/usr/bin/env bash
set -euo pipefail

API="http://localhost:8000"

echo "Stopping simulation..."
curl -sf -X POST "$API/admin/sim/stop" 2>/dev/null || true

echo "Stopping backend and frontend processes..."
# Find and stop uvicorn processes on port 8000
lsof -ti:8000 2>/dev/null | xargs -r kill 2>/dev/null || true
# Find and stop next dev processes on port 3000
lsof -ti:3000 2>/dev/null | xargs -r kill 2>/dev/null || true

echo "Done. Docker containers left running (postgres, redis)."
echo "To stop Docker: sudo docker stop courtops-db courtops-redis"

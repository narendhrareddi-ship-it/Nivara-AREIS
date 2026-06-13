#!/usr/bin/env bash
# Start the NIVARA Streamlit dashboard (port 8501).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="${HOME}/.local/bin:${PATH}"

export DB_HOST="${DB_HOST:-localhost}"
export DB_PORT="${DB_PORT:-5432}"
export ORCHESTRATOR_URL="${ORCHESTRATOR_URL:-http://localhost:8000}"
export VEO_MCP_URL="${VEO_MCP_URL:-http://localhost:8006}"

cd "${ROOT}/dashboard"
exec streamlit run app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true

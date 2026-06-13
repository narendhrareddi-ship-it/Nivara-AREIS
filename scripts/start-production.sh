#!/usr/bin/env bash
# Start NIVARA production backend (orchestrator + MCP servers)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

export DEFAULT_REGION="${DEFAULT_REGION:-Bangalore}"
export DEFAULT_STATE="${DEFAULT_STATE:-Karnataka}"
export DB_HOST="${DB_HOST:-aws-1-ap-south-1.pooler.supabase.com}"
export DB_PORT="${DB_PORT:-5432}"
export DB_NAME="${DB_NAME:-postgres}"
export USE_SUPABASE_STORAGE="${USE_SUPABASE_STORAGE:-true}"

echo "==> Installing agent package..."
pip3 install -q -e "$ROOT/agents" python-multipart 2>/dev/null || pip install -q -e "$ROOT/agents" python-multipart

echo "==> Ensuring Supabase Storage bucket..."
python3 "$ROOT/scripts/setup-supabase-storage.py" || echo "    (storage setup skipped — configure SUPABASE_* manually)"

SESSION="nivara-production"
TMUX_CONF="${TMUX_CONF:-/exec-daemon/tmux.portal.conf}"
tmux() { command tmux -f "$TMUX_CONF" "$@"; }

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "==> Stopping existing $SESSION session..."
  tmux kill-session -t "$SESSION"
fi

tmux new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-bash}" -l

start_service() {
  local name="$1"
  local port="$2"
  local cmd="$3"
  tmux new-window -t "$SESSION" -n "$name" -c "$ROOT" -- "${SHELL:-bash}" -l -c "
    export PORT=$port
    $cmd
  "
  echo "    Started $name on :$port"
}

tmux rename-window -t "$SESSION:0" social-mcp
tmux send-keys -t "$SESSION:0" "cd '$ROOT' && export PORT=8003 SOCIAL_MCP_PORT=8003 && python3 mcp-servers/social-mcp/server.py" C-m
echo "    Started social-mcp on :8003"

start_service veo-mcp 8006 "cd '$ROOT' && export PORT=8006 VEO_MCP_PORT=8006 SOCIAL_MCP_URL=http://localhost:8003 python3 mcp-servers/veo-mcp/server.py"
start_service orchestrator 8000 "cd '$ROOT/agents' && export PORT=8000 ORCHESTRATOR_PORT=8000 VEO_MCP_URL=http://localhost:8006 SOCIAL_MCP_URL=http://localhost:8003 nivara-orchestrator"

echo ""
echo "Production backend running in tmux session: $SESSION"
echo "  social-mcp     http://localhost:8003/health"
echo "  veo-mcp        http://localhost:8006/health"
echo "  orchestrator   http://localhost:8000/health"
echo ""
echo "Attach: tmux -f $TMUX_CONF attach -t $SESSION"

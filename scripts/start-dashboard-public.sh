#!/usr/bin/env bash
# Start dashboard and expose it on a public HTTPS URL (no Cursor port forwarding needed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URL_FILE="${ROOT}/dashboard.url"
LOG_FILE="${ROOT}/.dashboard-public-url.log"
CF_BIN="${CF_BIN:-/tmp/cloudflared}"

export PATH="${HOME}/.local/bin:${PATH}"

if ! curl -sf http://localhost:8501/_stcore/health >/dev/null 2>&1; then
  echo "Starting dashboard on port 8501..."
  SESSION_NAME="nivara-dashboard"
  tmux -f /exec-daemon/tmux.portal.conf has-session -t "=${SESSION_NAME}" 2>/dev/null \
    && tmux -f /exec-daemon/tmux.portal.conf kill-session -t "${SESSION_NAME}" 2>/dev/null || true
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "${SESSION_NAME}" -c "${ROOT}" \
    -- "${ROOT}/scripts/start-dashboard.sh"
  for _ in $(seq 1 20); do
    curl -sf http://localhost:8501/_stcore/health >/dev/null 2>&1 && break
    sleep 1
  done
fi

if [[ ! -x "${CF_BIN}" ]]; then
  echo "Downloading cloudflared..."
  curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "${CF_BIN}"
  chmod +x "${CF_BIN}"
fi

SESSION_NAME="dashboard-public-tunnel"
tmux -f /exec-daemon/tmux.portal.conf has-session -t "=${SESSION_NAME}" 2>/dev/null \
  && tmux -f /exec-daemon/tmux.portal.conf kill-session -t "${SESSION_NAME}" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "${SESSION_NAME}" -c "${ROOT}" \
  -- "${CF_BIN} tunnel --url http://localhost:8501 2>&1 | tee ${LOG_FILE}"

PUBLIC_URL=""
for _ in $(seq 1 30); do
  PUBLIC_URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "${LOG_FILE}" 2>/dev/null | head -1 || true)
  [[ -n "${PUBLIC_URL}" ]] && break
  sleep 1
done

if [[ -z "${PUBLIC_URL}" ]]; then
  echo "Failed to create public dashboard URL. Check ${LOG_FILE}"
  exit 1
fi

echo "${PUBLIC_URL}" > "${URL_FILE}"
echo ""
echo "=============================================="
echo " NIVARA Dashboard is live"
echo " Public URL: ${PUBLIC_URL}"
echo " Local URL:  http://localhost:8501 (VM only)"
echo " Saved to:   ${URL_FILE}"
echo "=============================================="
echo "Open the Public URL in your browser."

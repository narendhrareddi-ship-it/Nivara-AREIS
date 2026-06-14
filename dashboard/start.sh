#!/bin/sh
# Render sets PORT dynamically — Streamlit must bind to it or deploy fails.
set -e
PORT="${PORT:-8501}"
exec streamlit run streamlit_app.py \
  --server.port="${PORT}" \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false

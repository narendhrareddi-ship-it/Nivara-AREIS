#!/usr/bin/env bash
# Start local Ollama for NIVARA dev (docker or native install).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  echo "Starting Ollama via docker compose..."
  docker compose up -d ollama
  echo "Pulling llama3.2 (first run may take several minutes)..."
  docker exec nivara-ollama ollama pull llama3.2
elif command -v ollama >/dev/null 2>&1; then
  if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Starting ollama serve in background..."
    nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
    sleep 2
  fi
  echo "Pulling llama3.2..."
  ollama pull llama3.2
else
  echo "Install Ollama: https://ollama.com/download"
  echo "Or install Docker and run: docker compose up -d ollama"
  exit 1
fi

if curl -sf http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "Ollama is live at http://localhost:11434"
else
  echo "Ollama failed to start — check logs."
  exit 1
fi

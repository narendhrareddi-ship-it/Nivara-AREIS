FROM python:3.11-slim

WORKDIR /app

COPY agents/pyproject.toml agents/README.md /app/agents/
COPY agents/src /app/agents/src

RUN pip install --no-cache-dir -e /app/agents

ENV ORCHESTRATOR_HOST=0.0.0.0
ENV ORCHESTRATOR_PORT=8000
EXPOSE 8000

CMD ["nivara-orchestrator"]

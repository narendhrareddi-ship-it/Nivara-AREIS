FROM python:3.11-slim

WORKDIR /app

COPY agents/pyproject.toml agents/README.md /app/agents/
COPY agents/src /app/agents/src

RUN pip install --no-cache-dir -e /app/agents

ENV ORCHESTRATOR_HOST=0.0.0.0
ENV ORCHESTRATOR_PORT=8000
ENV DB_SSLMODE=require
ENV DB_HOST=aws-1-ap-south-1.pooler.supabase.com
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=postgres.mxjhwjxxqtkwsrwtqwuc
ENV SUPABASE_URL=https://mxjhwjxxqtkwsrwtqwuc.supabase.co
ENV DEFAULT_REGION=Bangalore
ENV DEFAULT_STATE=Karnataka
EXPOSE 8000

CMD ["nivara-orchestrator"]

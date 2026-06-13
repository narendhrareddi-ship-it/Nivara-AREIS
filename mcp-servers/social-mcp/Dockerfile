FROM python:3.11-slim

WORKDIR /app

COPY agents/pyproject.toml agents/README.md /app/agents/
COPY agents/src /app/agents/src
COPY mcp-servers/social-mcp /app/mcp-servers/social-mcp

RUN pip install --no-cache-dir -e /app/agents

ENV SOCIAL_MCP_PORT=8003
ENV DB_SSLMODE=require
ENV DB_HOST=aws-1-ap-south-1.pooler.supabase.com
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=postgres.mxjhwjxxqtkwsrwtqwuc
EXPOSE 8003

CMD ["python", "mcp-servers/social-mcp/server.py"]

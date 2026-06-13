FROM python:3.11-slim

WORKDIR /app

COPY agents/pyproject.toml agents/README.md /app/agents/
COPY agents/src /app/agents/src
COPY mcp-servers/veo-mcp /app/mcp-servers/veo-mcp

RUN pip install --no-cache-dir -e /app/agents \
    && pip install --no-cache-dir python-multipart

ENV VEO_MCP_PORT=8006
ENV DB_SSLMODE=require
ENV DB_HOST=aws-1-ap-south-1.pooler.supabase.com
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=postgres.mxjhwjxxqtkwsrwtqwuc
EXPOSE 8006

CMD ["python", "mcp-servers/veo-mcp/server.py"]

FROM python:3.11-slim

WORKDIR /app

# Root requirements (dashboard + editable agents)
COPY requirements.txt /app/requirements.txt
COPY agents/pyproject.toml agents/README.md /app/agents/
COPY agents/src /app/agents/src

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY dashboard /app/dashboard
COPY streamlit_app.py /app/streamlit_app.py
COPY .streamlit /app/.streamlit

ENV PYTHONUNBUFFERED=1
ENV DB_SSLMODE=require
ENV AUTO_SYNC_ON_LOAD=false
EXPOSE 8501

CMD [
  "streamlit", "run", "streamlit_app.py",
  "--server.port=8501",
  "--server.address=0.0.0.0",
  "--server.headless=true",
  "--browser.gatherUsageStats=false"
]

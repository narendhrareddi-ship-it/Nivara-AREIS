FROM python:3.11-slim

WORKDIR /app

# Lightweight Render build — no agents package (saves memory on free tier)
COPY requirements-render.txt /app/requirements-render.txt
RUN pip install --no-cache-dir -r /app/requirements-render.txt

COPY dashboard /app/dashboard
COPY streamlit_app.py /app/streamlit_app.py
COPY .streamlit /app/.streamlit

ENV PYTHONUNBUFFERED=1
ENV DB_SSLMODE=require
ENV AUTO_SYNC_ON_LOAD=false
ENV AUTO_SYNC_PIPELINE=false

# Render injects PORT; must not hardcode 8501
CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false --server.enableCORS=false --server.enableXsrfProtection=false"]

FROM python:3.11-slim

WORKDIR /app

# Lightweight Render build — no agents package (saves memory on free tier)
COPY requirements-render.txt /app/requirements-render.txt
RUN pip install --no-cache-dir -r /app/requirements-render.txt

COPY dashboard /app/dashboard
COPY streamlit_app.py /app/streamlit_app.py
COPY .streamlit /app/.streamlit
COPY dashboard/start.sh /app/dashboard/start.sh
RUN chmod +x /app/dashboard/start.sh

ENV PYTHONUNBUFFERED=1
ENV DB_SSLMODE=require
ENV AUTO_SYNC_ON_LOAD=false
ENV AUTO_SYNC_PIPELINE=false

EXPOSE 8501

CMD ["/app/dashboard/start.sh"]

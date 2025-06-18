FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock* ./
COPY server ./server

RUN python -m venv .venv \
    && . .venv/bin/activate \
    && pip install --no-cache-dir --upgrade pip \
    && pip install uv \
    && uv sync

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "server.start_server_http:app", "--port", "8000", "--host", "0.0.0.0"]

EXPOSE 8000
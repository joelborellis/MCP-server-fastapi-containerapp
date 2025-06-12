FROM python:3.13-slim

WORKDIR /

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Install uv and dependencies from pyproject.toml
RUN pip install uv 
RUN pip install fastapi[standard]
RUN pip install mcp



# Run the application.
CMD ["uvicorn", "start_server_http:app", "--port", "8000", "--host", "0.0.0.0"]


EXPOSE 8000
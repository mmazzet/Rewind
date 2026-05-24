FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/backend

COPY . .

RUN pip install uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync

CMD ["uv", "run", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
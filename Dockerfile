FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim
WORKDIR /app

ENV PYTHONPATH=/app
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .

CMD ["uv", "run", "uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "8000"]

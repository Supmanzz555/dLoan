FROM ghcr.io/astral-sh/uv:python3.12-slim
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .
# In Docker, services override this command per container
CMD ["uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "8000"]

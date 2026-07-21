# syntax=docker/dockerfile:1

# ---- builder: resolve dependencies into a venv only ----
FROM python:3.14-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

# Copied alone first so this layer only rebuilds when dependencies change,
# not on every source-code edit.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---- runtime: minimal image, non-root, no build tools ----
FROM python:3.14-slim AS runtime

RUN useradd --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker/backend/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh && chown -R appuser:appuser /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# Reuses the existing /health endpoint (already checks real DB
# connectivity) — no separate health-check logic invented for Docker.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health', timeout=3).status == 200 else 1)"

ENTRYPOINT ["./entrypoint.sh"]

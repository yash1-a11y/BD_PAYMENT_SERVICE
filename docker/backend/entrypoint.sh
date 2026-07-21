#!/bin/sh
set -e

# Migrations are a deliberate, separate step in this project's existing
# convention (every phase's "run it yourself" docs run `alembic upgrade
# head` manually) — never assumed safe to run automatically on every
# container start. Opt in explicitly per-environment if you want it here.
if [ "${RUN_MIGRATIONS_ON_STARTUP:-false}" = "true" ]; then
  echo "RUN_MIGRATIONS_ON_STARTUP=true — running alembic upgrade head..."
  alembic upgrade head
fi

exec uvicorn src.app:app --host 0.0.0.0 --port 8000

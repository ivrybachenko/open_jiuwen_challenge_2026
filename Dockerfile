# syntax=docker/dockerfile:1
#
# Pinned base image (multi-arch index digest):
#   python:3.12-slim
FROM python:3.12-slim@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54

# Pinned uv release, only the binaries are copied into the image.
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:${PATH}" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never \
    HOME=/tmp \
    TMPDIR=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    XDG_CONFIG_HOME=/tmp/.config

WORKDIR /app

# Dependencies first so source-only changes reuse this layer.
COPY harness/pyproject.toml harness/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project \
        --python /usr/local/bin/python3.12

# The src-layout package is installed into /app/.venv by the second sync.
# /app/run_agent.py is the path hardcoded by the jury.
COPY harness/src ./src
COPY harness/src/harness/run_agent.py ./run_agent.py
RUN uv sync --frozen --no-dev --python /usr/local/bin/python3.12

# The harness is started read-only (`--read-only --tmpfs /tmp`), so all runtime
# state must live under /tmp. Tasks are mounted rw at /data/tasks.
ENTRYPOINT ["python", "/app/run_agent.py"]
CMD ["--tasks-dir", "/data/tasks"]

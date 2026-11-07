# syntax=docker/dockerfile:1
#
# Pinned base image (multi-arch index digest):
#   python:3.12-slim
FROM python:3.12-slim@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54

# Pinned uv release, only the binaries are copied into the image.
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
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

# Dependencies first so source-only changes reuse this layer. The venv lives at
# /app/.venv and is the first entry in PATH, so the jury's `--entrypoint python`
# resolves to the venv interpreter with all dependencies available.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project \
        --python /usr/local/bin/python3.12

# The whole src/ tree becomes /app, so the jury's hardcoded
# `python /app/run_agent.py` keeps working.
COPY src ./

# The harness is started read-only (`--read-only --tmpfs /tmp`), so all runtime
# state must live under /tmp. Tasks are mounted rw at /data/tasks.
ENTRYPOINT ["python", "/app/run_agent.py"]
CMD ["--tasks-dir", "/data/tasks"]

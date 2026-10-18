# Multi-stage Dockerfile for Aether AI Platform
FROM python:3.12-slim-bookworm AS builder

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies first for layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source
COPY . .
RUN uv sync --frozen --no-dev

# Production runtime stage
FROM python:3.12-slim-bookworm AS runner

WORKDIR /app

# Install runtime audio dependencies (libportaudio2 for sounddevice / TTS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment and application code from builder
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["aether", "serve", "--host", "0.0.0.0", "--port", "8000"]

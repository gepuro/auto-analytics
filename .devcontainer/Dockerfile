# Auto Analytics Development Container
FROM python:3.11.6-slim

# Set environment variables
ENV PYTHONPATH=/workspace \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies and uv (Python package manager)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Create workspace directory
WORKDIR /workspace

# Copy project configuration files
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen --no-install-project

# Set up development environment
ENV UV_PROJECT_ENVIRONMENT=/workspace/.venv
ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="/workspace/.venv/bin:$PATH"

# Install development dependencies
RUN uv sync --group dev --frozen --no-install-project

# Set working directory
WORKDIR /workspace

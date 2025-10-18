# Multi-stage build for production deployment
FROM python:3.10-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Set environment
ENV PATH="/app/.venv/bin:$PATH"

# Run server
CMD ["python", "server.py"]


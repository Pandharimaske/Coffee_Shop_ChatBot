# Stage 1: Build environment
FROM python:3.11-slim as builder

# Install uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install dependencies (frozen) into a virtual environment
# We skip installing the project itself as a package to save space
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime environment
FROM python:3.11-slim

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Ensure the virtual environment's bin is in the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application code
COPY . .

# Expose the API port
EXPOSE 8000

# Start the server using gunicorn with uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "api.main:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120"]

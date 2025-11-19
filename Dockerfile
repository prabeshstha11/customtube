FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv pip install --system .

# Copy application code
COPY . .

# Expose the port
EXPOSE 5551

# Run the application
CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "5551"]

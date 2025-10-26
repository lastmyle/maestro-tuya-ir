FROM public.ecr.aws/docker/library/python:3.14.0-alpine

WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    curl

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"
ENV UV_SYSTEM_PYTHON=1

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv (fallback if uv.lock doesn't exist)
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

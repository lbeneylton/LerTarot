# Stage 1: Build & Dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies required for building Python packages (like psycopg)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Configure poetry to not create a virtual environment, as the container itself provides isolation
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (only main dependencies, no dev dependencies)
RUN poetry install --only main --no-interaction --no-ansi

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime system dependencies for psycopg
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY ./src ./src
COPY ./alembic.ini ./
COPY ./alembic ./alembic
COPY ./scripts ./scripts

# Make entrypoint executable
RUN chmod +x ./scripts/entrypoint.sh

# Expose port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app/src

# Entrypoint script will run migrations and then start the command
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command (starts FastAPI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

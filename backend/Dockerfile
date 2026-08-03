FROM python:3.12-slim

# Metadata
LABEL description="Institutional requests management API"

# Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app/backend

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ .

# Entry script that runs migrations and then starts the server
COPY entrypoint.sh /app/backend/entrypoint.sh
# Strip Windows CRLF line endings so the shebang works on Linux
RUN sed -i 's/\r$//' /app/backend/entrypoint.sh && chmod +x /app/backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/backend/entrypoint.sh"]

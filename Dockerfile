# ============================================================================
# BASE IMAGE - Optimized for AWS ECR
# ============================================================================

FROM python:3.12-slim

# ============================================================================
# METADATA
# ============================================================================

LABEL maintainer="AI E-Commerce Analytics"
LABEL description="AI-Powered E-Commerce Analytics & Recommendation Engine"
LABEL version="1.0.0"

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
WORKDIR /app

# ============================================================================
# SYSTEM DEPENDENCIES
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# PYTHON DEPENDENCIES
# ============================================================================

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================================================
# APPLICATION
# ============================================================================

COPY . .

# Create necessary directories
RUN mkdir -p logs && chmod 755 logs

# ============================================================================
# EXPOSE & HEALTH CHECK
# ============================================================================

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ============================================================================
# START APPLICATION
# ============================================================================

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

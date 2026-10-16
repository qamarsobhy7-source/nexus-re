# NEXUS-RE Dockerfile
# Multi-stage build for a minimal production image

FROM python:3.13-slim AS builder

WORKDIR /app

# Copy dependencies list
COPY requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================================

FROM python:3.13-slim

LABEL maintainer="Qamar Sobhy"
LABEL description="NEXUS-RE: AI-Powered Reverse Engineering Platform"
LABEL version="3.0"
LABEL license="MIT"

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY nexus_re_v3.py .
COPY README.md .
COPY proposal.md .

# Set up environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV NEXUS_LOG_LEVEL=INFO

# Create non-root user for security
RUN useradd -m -u 1000 nexus && chown -R nexus:nexus /app
USER nexus

# Default command
CMD ["python", "nexus_re_v3.py"]

# Usage:
#   docker build -t nexus-re:latest .
#   docker run -it --rm nexus-re:latest
#   docker run -it --rm -v $(pwd)/samples:/samples nexus-re:latest
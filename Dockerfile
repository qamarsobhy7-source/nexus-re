FROM python:3.11-slim

LABEL maintainer="Qamar Sobhy"
LABEL description="NEXUS-RE: AI-Powered Reverse Engineering Platform"
LABEL version="3.0"

WORKDIR /app

# NEXUS-RE has ZERO runtime dependencies (pure Python stdlib 3.11+).
# No pip install needed.
COPY nexus_re_v3.py .
COPY nexus_agents.py .
COPY nexus_rag.py .
COPY api_render.py .
COPY README.md .

# Non-root user for security
RUN useradd -m -u 1000 nexus && chown -R nexus:nexus /app
USER nexus

ENV PYTHONUNBUFFERED=1
ENV PYTHON_VERSION=3.11.9
ENV PORT=8000

EXPOSE 8000

CMD ["python", "api_render.py"]

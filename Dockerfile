FROM python:3.11-slim

LABEL maintainer="Qamar Sobhy"
LABEL description="NEXUS-RE: AI-Powered Reverse Engineering Platform"
LABEL version="3.0"

WORKDIR /app

# Copy all Python files
COPY nexus_re_v3.py .
COPY nexus_agents.py .
COPY nexus_rag.py .
COPY api_render.py .
COPY README.md .
COPY proposal.md .

# Non-root user
RUN useradd -m -u 1000 nexus && chown -R nexus:nexus /app
USER nexus

ENV PYTHONUNBUFFERED=1
ENV PYTHON_VERSION=3.11.9
ENV PORT=8000

EXPOSE 8000

# Run the API (not the CLI)
CMD ["python", "api_render.py"]

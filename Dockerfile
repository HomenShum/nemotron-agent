# ── Nemotron 3 Ultra Agent — LangGraph + FastAPI ──────────────────────────
# Base: slim Python 3.11 on Debian Bookworm
FROM python:3.11-slim-bookworm

# Metadata
LABEL org.opencontainers.image.title="Nemotron 3 Ultra Agent"
LABEL org.opencontainers.image.description="LangGraph + FastAPI agent powered by Nemotron 3 Ultra on GMI Cloud Agentbox"
LABEL org.opencontainers.image.source="https://github.com/gmi-nemotron-agent/nemotron-agent"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 agent
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER agent

# GMI Agentbox injects these at runtime — do not hardcode
ENV GMI_MAAS_BASE_URL="https://api.gmi-serving.com"
ENV GMI_MODELS="nvidia/nemotron-3-ultra-550b-a55b"
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port (GMI default: 8080 → 443)
EXPOSE 8080

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]

# Claude Memory MCP Server
# Supports both stdio (local) and HTTP (cloud) transports
#
# SECURITY WARNING: This server does NOT implement authentication.
# For production use, deploy behind a reverse proxy with auth
# (Railway private networking, Cloudflare Access, etc.)

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --no-cache-dir .

# Configure for HTTP transport by default in container
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=3000

# Authentication: Set API_TOKEN via deployment platform env vars
# DO NOT set tokens in Dockerfile - use Railway/Fly.io secrets

# Memory storage location (mount persistent volume here)
ENV CLAUDE_MEMORY_PATH=/data/claude-memory

# Create data directory
RUN mkdir -p /data/claude-memory

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Run server
CMD ["python", "-m", "claude_memory_mcp"]

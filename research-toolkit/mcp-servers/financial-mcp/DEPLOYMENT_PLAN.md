# Financial MCP Server - Online Deployment Plan

**Goal**: Convert local-only stdio server to online streamable HTTP server
**Current Status**: Local stdio transport only
**Target Status**: Deployed HTTP server accessible from anywhere
**Created**: 2025-11-22

---

## Quick Start (Deploy in ~1 Hour)

**TL;DR**: Add HTTP transport → test locally → deploy to Railway → connect Claude Code

```bash
# 1. Add HTTP transport (see Phase 1.1 below for code)
# Edit financial_server.py to support dual transport (stdio + HTTP)

# 2. Test locally
MCP_TRANSPORT=http MCP_PORT=3000 python financial_server.py

# 3. Push to GitHub
git add .
git commit -m "Add HTTP transport for deployment"
git push

# 4. Deploy to Railway
# - Go to railway.app
# - New Project → Deploy from GitHub
# - Select this repository
# - Set environment variable: MCP_TRANSPORT=http
# - Deploy (Railway auto-detects Python)

# 5. Configure Claude Code
claude mcp add --transport http financial https://your-app.railway.app

# Done! Your server is now accessible online.
```

**Read below for detailed instructions, alternatives, and production enhancements.**

---

## Overview

This server currently uses `stdio` transport (subprocess-based, local only). To make it work online, we need to:
1. Add streamable HTTP transport support
2. Deploy to a hosting service
3. Configure remote access

---

## Phase 1: Add HTTP Transport Support

### 1.1 Update financial_server.py

**Current implementation** (stdio):
```python
async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
```

**New implementation** (dual transport):
```python
import os
import mcp.server.streamable_http as streamable_http

async def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        # HTTP transport for remote access
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "3000"))

        print(f"Starting HTTP server on {host}:{port}")
        await streamable_http.run(server, host=host, port=port)
    else:
        # stdio transport for local development
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="financial-data-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
```

**Benefits of dual transport**:
- Keep stdio for local testing
- Enable HTTP for remote deployment
- Switch via environment variable

### 1.2 Update requirements.txt

Check if HTTP transport requires additional dependencies:
```bash
# Current dependencies
mcp>=0.9.0
yfinance
pandas
numpy
```

May need to verify HTTP support is included in current MCP SDK version.

### 1.3 Test locally

```bash
# Test HTTP mode locally
MCP_TRANSPORT=http MCP_PORT=3000 python financial_server.py

# Test connection (in another terminal)
curl http://localhost:3000

# Test stdio mode still works
python financial_server.py
```

---

## Phase 2: Containerization (Optional but Recommended)

### 2.1 Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY . .

# Expose HTTP port
EXPOSE 3000

# Set environment for HTTP transport
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=3000

# Run server
CMD ["python", "financial_server.py"]
```

### 2.2 Create .dockerignore

```
__pycache__/
*.pyc
*.pyo
*.db
.git/
.env
venv/
*.md
tests/
```

### 2.3 Create docker-compose.yml

```yaml
version: '3.8'

services:
  financial-mcp:
    build: .
    ports:
      - "3000:3000"
    environment:
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=3000
    volumes:
      - ./cache:/app/cache  # Persist cache
    restart: unless-stopped
```

### 2.4 Test Docker locally

```bash
# Build and run
docker-compose up --build

# Test connection
curl http://localhost:3000

# Check logs
docker-compose logs -f
```

---

## Phase 3: Choose Deployment Target

### Option A: Railway.app (Recommended - Easiest)

**Pros**:
- GitHub integration (auto-deploy on push)
- Free tier available
- Simple setup
- Built-in HTTPS

**Setup**:
1. Sign up at railway.app
2. Create new project
3. Connect GitHub repository
4. Set environment variables:
   - `MCP_TRANSPORT=http`
   - `MCP_HOST=0.0.0.0`
   - `MCP_PORT=3000`
5. Railway auto-detects Python and deploys

**Cost**: Free tier, then ~$5/month

### Option B: Fly.io (Docker-focused)

**Pros**:
- Excellent Docker support
- Free tier (3 shared VMs)
- Global edge deployment
- Simple CLI

**Setup**:
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app (creates fly.toml)
fly launch

# Deploy
fly deploy
```

**Cost**: Free tier, then pay-as-you-go

### Option C: Render.com (Simple PaaS)

**Pros**:
- GitHub integration
- Free tier
- Simple dashboard
- Automatic SSL

**Setup**:
1. Sign up at render.com
2. New Web Service
3. Connect GitHub repo
4. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `python financial_server.py`
   - Environment vars: `MCP_TRANSPORT=http`
5. Deploy

**Cost**: Free tier available

### Option D: VPS (Most control, most work)

**Providers**: DigitalOcean, Linode, Hetzner
**Setup**: Docker + nginx reverse proxy + SSL certificates
**Cost**: $5-10/month
**Complexity**: High

---

## Phase 4: Deployment Execution

### 4.1 Pre-deployment checklist

- [ ] HTTP transport tested locally
- [ ] Docker build succeeds
- [ ] Environment variables documented
- [ ] Cache directory handling decided (persistent vs ephemeral)
- [ ] Hosting provider account created
- [ ] Repository pushed to GitHub

### 4.2 Deploy

**For Railway**:
1. Go to railway.app
2. New Project → Deploy from GitHub
3. Select repository
4. Set environment variables
5. Deploy

**For Fly.io**:
```bash
fly launch
fly deploy
fly open
```

**For Render**:
1. New Web Service
2. Connect repo
3. Configure build/start commands
4. Deploy

### 4.3 Verify deployment

```bash
# Get your deployment URL (example: https://financial-mcp.railway.app)
DEPLOY_URL="your-url-here"

# Test health (should get MCP server response)
curl $DEPLOY_URL

# Note the URL for Claude Code configuration
```

---

## Phase 5: Configure Claude Code to Use Remote Server

### 5.1 Add remote server

```bash
# Add HTTP server to Claude Code
claude mcp add --transport http financial-server https://your-app.railway.app

# With authentication (if you add API key later)
claude mcp add --transport http financial-server \
  --header "X-Api-Key: your-secret-key" \
  https://your-app.railway.app
```

### 5.2 Test tools

In Claude Code or Claude Desktop:
```
User: "Get the stock price for AAPL"
Claude: [Uses remote financial-server tool]
```

### 5.3 Remove local stdio version

If migration successful:
```bash
claude mcp remove financial-data-server  # Old local version
```

---

## Phase 6: CI/CD Automation (Optional)

### 6.1 GitHub Actions for Railway

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

**Setup**:
1. Get Railway token from dashboard
2. Add as GitHub secret: `RAILWAY_TOKEN`
3. Push to trigger deploy

### 6.2 GitHub Actions for Fly.io

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

---

## Phase 7: Production Enhancements (Future)

### 7.1 Add authentication

```python
# In financial_server.py - add middleware for API key validation
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

# Validate X-Api-Key header
```

### 7.2 Add monitoring

- Health check endpoint
- Prometheus metrics
- Error tracking (Sentry)
- Usage analytics

### 7.3 Add rate limiting

```python
# Prevent abuse
from slowapi import Limiter
```

### 7.4 Improve caching

- Redis instead of SQLite for distributed cache
- Cache warming strategies
- Cache invalidation webhooks

### 7.5 Scale horizontally

- Multiple instances behind load balancer
- Shared Redis cache
- Session affinity if needed

---

## Implementation Timeline

### Minimal viable deployment (1-2 hours)
1. Add HTTP transport to financial_server.py (15 min)
2. Test locally (15 min)
3. Deploy to Railway (30 min)
4. Configure Claude Code (15 min)
5. Test end-to-end (15 min)

### Production-ready deployment (4-6 hours)
1. Minimal viable deployment (1-2 hours)
2. Add Dockerfile (30 min)
3. Set up CI/CD (1 hour)
4. Add authentication (1 hour)
5. Add monitoring (1-2 hours)
6. Documentation and testing (1 hour)

---

## Cost Estimates

| Option | Free Tier | Paid Tier |
|--------|-----------|-----------|
| Railway | Limited hours | ~$5/month |
| Fly.io | 3 VMs free | Pay-as-you-go |
| Render | 750 hours/month | $7/month |
| DigitalOcean VPS | None | $5/month |

**Recommendation**: Start with Railway or Fly.io free tier

---

## Rollback Plan

If deployment fails or issues arise:

1. **Keep stdio version working** - dual transport ensures local version still functions
2. **Remove remote server** from Claude Code config
3. **Debug locally** using HTTP mode: `MCP_TRANSPORT=http python financial_server.py`
4. **Check logs** in hosting dashboard
5. **Test with curl** before connecting Claude

---

## Success Criteria

- [ ] Server responds to HTTP requests
- [ ] All 6 tools work remotely
- [ ] Cache persists between requests
- [ ] Response times < 5 seconds
- [ ] Claude Code can discover and use tools
- [ ] No errors in hosting logs
- [ ] Cost within budget

---

## Next Steps

**Immediate**:
1. Review this plan
2. Choose deployment option (recommend Railway)
3. Implement Phase 1 (HTTP transport)
4. Test locally
5. Deploy to hosting service

**After successful deployment**:
1. Document actual deployment experience
2. Update this plan with learnings
3. Consider CI/CD automation
4. Plan production enhancements

---

## References

- [MCP Deployment Guide](../../../docs/mcp-servers/deployment-guide.md)
- [MCP Official Spec](https://spec.modelcontextprotocol.io/)
- [Railway Docs](https://docs.railway.app/)
- [Fly.io Docs](https://fly.io/docs/)
- [Render Docs](https://render.com/docs)

---

## Notes

- SSE transport is deprecated - use streamable HTTP
- Dual transport approach allows local testing + remote deployment
- Start simple, add features incrementally
- Monitor costs and usage during initial deployment
- Cache persistence may require volume mounting

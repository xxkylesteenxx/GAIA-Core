# GAIA Python service — multi-stage container image.
# Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §4, DEP-001
#
# Build:   docker build -t gaia-server:dev -f docker/python/Dockerfile .
# Run:     docker run --rm -p 8080:8080 gaia-server:dev

# ---- Stage 1: build --------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies in an isolated prefix so they are copyable
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: runtime ------------------------------------------------------
FROM python:3.12-slim

LABEL org.opencontainers.image.title="gaia-server" \
      org.opencontainers.image.description="GAIA Python inference/coordination service" \
      org.opencontainers.image.vendor="GAIA Project" \
      org.opencontainers.image.source="https://github.com/xxkylesteenxx/GAIA-Core"

WORKDIR /app

# Copy installed packages from build stage only (DEP-001: no build toolchain in runtime)
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Non-root runtime user (spec §4: non-root runtime users)
RUN useradd --system --uid 1001 --no-create-home gaia
USER gaia

# Health check — liveness probe for Kubernetes (spec §4)
HEALTHCHECK \
  --interval=30s \
  --timeout=5s  \
  --start-period=10s \
  --retries=3   \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

EXPOSE 8080

ENTRYPOINT ["python", "-m", "gaia_server"]

# syntax=docker/dockerfile:1
# GAIA Rust service — canonical multi-stage image.
#
# Build context: repository root (or service directory with Cargo.toml)
# Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §4, DEP-001
#
# Usage:
#   docker build -t gaia-service:dev -f docker/rust/Dockerfile .
#   docker run --rm -p 8081:8081 gaia-service:dev

# ---- Stage 1: build --------------------------------------------------------
FROM rust:1.86-bookworm AS build

WORKDIR /build

# Copy manifest files first to maximise layer cache reuse:
# dependency compilation is re-run only when Cargo.toml or Cargo.lock changes.
COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release

# ---- Stage 2: runtime ------------------------------------------------------
# debian:bookworm-slim provides a shell and standard tools for:
#   - SPIRE workload API (unix socket interaction)
#   - runtime debugging with exec
#   - liveness probe scripts if needed
# Switch to gcr.io/distroless/cc-debian12 for a minimal attack surface
# once the service is stable and no shell access is required.
FROM debian:bookworm-slim AS runtime

LABEL org.opencontainers.image.title="gaia-service" \
      org.opencontainers.image.description="GAIA Rust core service" \
      org.opencontainers.image.source="https://github.com/xxkylesteenxx/GAIA-Core"

# Install runtime CA certificates for TLS (SPIFFE SVID verification)
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Non-root system user (spec §4: non-root runtime users)
RUN useradd --system --create-home --shell /usr/sbin/nologin gaia

WORKDIR /app

COPY --from=build /build/target/release/gaia-service /usr/local/bin/gaia-service

USER gaia

EXPOSE 8081

CMD ["/usr/local/bin/gaia-service"]

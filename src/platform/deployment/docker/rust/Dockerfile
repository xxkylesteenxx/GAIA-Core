# GAIA Rust service — multi-stage container image.
# Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §4, DEP-001
#
# Build:   docker build -t gaia-desktop-runtime:dev -f docker/rust/Dockerfile .
# Run:     docker run --rm gaia-desktop-runtime:dev

# ---- Stage 1: build --------------------------------------------------------
FROM rust:1.77-slim AS builder

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libssl-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Cache dependency compilation layer separately from source
COPY Cargo.toml Cargo.lock ./
# Dummy main to compile deps before copying real source
RUN mkdir src && echo 'fn main(){}' > src/main.rs \
  && cargo build --release --locked \
  && rm -rf src

# Copy and build real source
COPY src ./src
RUN touch src/main.rs && cargo build --release --locked

# ---- Stage 2: runtime (distroless, minimal attack surface) -----------------
FROM gcr.io/distroless/cc-debian12

LABEL org.opencontainers.image.title="gaia-desktop-runtime" \
      org.opencontainers.image.description="GAIA Rust desktop runtime service" \
      org.opencontainers.image.vendor="GAIA Project" \
      org.opencontainers.image.source="https://github.com/xxkylesteenxx/GAIA-Core"

# Non-root user provided by distroless base (uid 65532 = nonroot)
COPY --from=builder /build/target/release/gaia_service /gaia_service

USER nonroot

ENTRYPOINT ["/gaia_service"]

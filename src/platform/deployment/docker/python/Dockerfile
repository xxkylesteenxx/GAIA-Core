# syntax=docker/dockerfile:1
# GAIA Python service — canonical single-stage image.
# Dedicated variant for services with a custom requirements.txt.
#
# Build context: src/platform/deployment/
# Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §4, DEP-001
#
# Usage:
#   docker build -t gaia-server:dev -f docker/python/Dockerfile .

FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="gaia-server" \
      org.opencontainers.image.description="GAIA Python inference/coordination service" \
      org.opencontainers.image.source="https://github.com/xxkylesteenxx/GAIA-Core"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system gaia && adduser --system --ingroup gaia gaia

COPY docker/python/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

COPY src/ /app/

USER gaia

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import socket; s=socket.create_connection(('127.0.0.1',8080),2); s.close()"

CMD ["python", "-m", "gaia_server"]

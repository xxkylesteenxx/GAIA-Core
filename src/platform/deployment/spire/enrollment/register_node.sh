#!/usr/bin/env bash
# GAIA SPIRE — bootstrap node attestation via join token.
# Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §9, DEP-005/DEP-006
#
# IMPORTANT: Join token attestation is for dev/CI only.
# Replace with TPM devID or k8s_psat attestation for production (spec §9, table).
#
# Usage:
#   ./register_node.sh <node-hostname>

set -euo pipefail

NODE_HOST="${1:?Usage: $0 <node-hostname>}"
TRUST_DOMAIN="gaia.local"  # REPLACE_ME

echo "[GAIA] Generating join token for node: ${NODE_HOST}"

TOKEN=$(spire-server token generate -spiffeID \
  "spiffe://${TRUST_DOMAIN}/agent/join_token/${NODE_HOST}" \
  | awk '/^Token/{print $2}')

echo "[GAIA] Join token: ${TOKEN}"
echo "[GAIA] Run on target node:"
echo "  spire-agent run -config /opt/spire/conf/agent/agent.conf -joinToken ${TOKEN}"
echo
echo "[GAIA] NOTE: join_token is for dev/CI only. Use TPM/PSAT in production."

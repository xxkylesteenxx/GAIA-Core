#!/usr/bin/env bash
# GAIA SPIRE — register a workload SPIFFE entry.
# Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §9, DEP-006
#
# Usage:
#   ./register_workload.sh <service-name> <unix-uid>
#
# Example:
#   ./register_workload.sh gaia-server 1001
#
# Requires: spire-server CLI available on PATH and server reachable.

set -euo pipefail

SERVICE_NAME="${1:?Usage: $0 <service-name> <unix-uid>}"
UNIX_UID="${2:?Usage: $0 <service-name> <unix-uid>}"

TRUST_DOMAIN="gaia.local"        # REPLACE_ME
SPIFFE_ID="spiffe://${TRUST_DOMAIN}/workload/${SERVICE_NAME}"
PARENT_ID="spiffe://${TRUST_DOMAIN}/agent/join_token/TOKEN"  # REPLACE_ME

echo "[GAIA] Registering workload SPIFFE entry:"
echo "  SPIFFE ID : ${SPIFFE_ID}"
echo "  Parent ID : ${PARENT_ID}"
echo "  Unix UID  : ${UNIX_UID}"

spire-server entry create \
  -spiffeID  "${SPIFFE_ID}" \
  -parentID  "${PARENT_ID}" \
  -selector  "unix:uid:${UNIX_UID}"

echo "[GAIA] Workload entry registered."

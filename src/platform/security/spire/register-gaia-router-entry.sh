#!/usr/bin/env bash
set -euo pipefail

: "${SPIFFE_ID:=spiffe://gaia.internal/workload/gaia-router}"
: "${PARENT_ID:=spiffe://gaia.internal/spire/agent/k8s_psat/gaia-cluster/node/placeholder}"
: "${NAMESPACE:=gaia-system}"
: "${SERVICE_ACCOUNT:=gaia-router}"

cat <<CMD
spire-server entry create \\
  -spiffeID "$SPIFFE_ID" \\
  -parentID "$PARENT_ID" \\
  -selector k8s:ns:$NAMESPACE \\
  -selector k8s:sa:$SERVICE_ACCOUNT
CMD

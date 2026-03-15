#!/usr/bin/env bash
set -euo pipefail

TPM_DEVICE="${TPM_DEVICE:-/dev/tpmrm0}"
IDENTITY_DIR="${IDENTITY_DIR:-/opt/gaia/identity}"

mkdir -p "$IDENTITY_DIR"

if [[ ! -e "$TPM_DEVICE" ]]; then
  echo "TPM device not found at $TPM_DEVICE" >&2
  exit 1
fi

cat > "$IDENTITY_DIR/README.txt" <<TXT
This directory is reserved for GAIA node identity artifacts.
Provisioning of TPM-backed identity requires deployment-specific tooling,
endorsement verification policy, and the selected SPIRE TPM plugin binary.
TXT

echo "GAIA TPM bootstrap placeholder completed for $TPM_DEVICE"

#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
#
# unload_scx.sh
#
# Safely unloads the GAIA sched_ext scheduler by unpinning the BPF
# object from the BPF filesystem. Once the last reference to the
# struct_ops map is dropped, the kernel reverts to CFS automatically.
#
# Usage:
#   sudo ./unload_scx.sh

set -euo pipefail

BPF_PIN_DIR="/sys/fs/bpf/gaia_scx"

if [[ $EUID -ne 0 ]]; then
  echo "[gaia] error: must be run as root" >&2
  exit 1
fi

# Remove the pinned struct_ops link first, then the directory.
if [[ -e "${BPF_PIN_DIR}/gaia_ops" ]]; then
  echo "[gaia] unpinning ${BPF_PIN_DIR}/gaia_ops"
  rm -f "${BPF_PIN_DIR}/gaia_ops"
else
  echo "[gaia] ${BPF_PIN_DIR}/gaia_ops not found — already unloaded?"
fi

if [[ -d "${BPF_PIN_DIR}" ]]; then
  echo "[gaia] removing pin directory ${BPF_PIN_DIR}"
  rmdir "${BPF_PIN_DIR}" || true
fi

echo "[gaia] sched_ext state:"
cat /sys/kernel/sched_ext/state 2>/dev/null || echo "(sched_ext state unavailable)"

echo "[gaia] done — scheduler reverted to CFS"

#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
#
# build_scx.sh
#
# Conservative helper for a version-pinned sched_ext workflow.
# Assumes:
#   - Linux kernel with CONFIG_SCHED_CLASS_EXT=y
#   - bpftool, clang, and pahole/BTF support installed
#   - Root privileges (for struct_ops register)
#
# Usage:
#   sudo ./build_scx.sh
#   BPF_CLANG=clang-17 sudo -E ./build_scx.sh

set -euo pipefail

BPF_CLANG="${BPF_CLANG:-clang}"
BPFTOOL="${BPFTOOL:-bpftool}"
ARCH_TOKEN="${ARCH_TOKEN:-x86}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── Preflight checks ──────────────────────────────────────────────────────────

if [[ $EUID -ne 0 ]]; then
  echo "[gaia] error: must be run as root (needed for struct_ops register)" >&2
  exit 1
fi

if [[ ! -f /sys/kernel/btf/vmlinux ]]; then
  echo "[gaia] error: /sys/kernel/btf/vmlinux not found" >&2
  echo "[gaia]        kernel must be built with CONFIG_DEBUG_INFO_BTF=y" >&2
  exit 1
fi

if ! grep -q 'SCHED_CLASS_EXT' /boot/config-"$(uname -r)" 2>/dev/null; then
  echo "[gaia] warning: CONFIG_SCHED_CLASS_EXT not confirmed in running kernel config" >&2
fi

# ── Build ─────────────────────────────────────────────────────────────────────

if [[ ! -f vmlinux.h ]]; then
  echo "[gaia] generating vmlinux.h from /sys/kernel/btf/vmlinux"
  "$BPFTOOL" btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
fi

echo "[gaia] building BPF object (arch=${ARCH_TOKEN})"
"$BPF_CLANG" \
  -target bpf \
  -D__TARGET_ARCH_"${ARCH_TOKEN}" \
  -g -O2 \
  -c gaia_scx.bpf.c \
  -o gaia_scx.bpf.o \
  -I.

# ── Load ──────────────────────────────────────────────────────────────────────

echo "[gaia] registering sched_ext struct_ops"
"$BPFTOOL" struct_ops register gaia_scx.bpf.o /sys/fs/bpf/gaia_scx

echo "[gaia] active scheduler:"
cat /sys/kernel/sched_ext/root/ops

echo "[gaia] done — GAIA sched_ext scheduler is live"

#!/usr/bin/env bash
# setup_cgroups.sh — Create GAIA cgroup v2 hierarchy
#
# Creates per-core cgroups under /sys/fs/cgroup/gaia/ with
# CPU and memory reservations for each GAIA consciousness core.
#
# Usage: sudo bash platform/kernel/cgroups/setup_cgroups.sh
# Undo:  sudo bash platform/kernel/cgroups/setup_cgroups.sh --teardown

set -euo pipefail

CGROUP_ROOT="/sys/fs/cgroup/gaia"
TEARDOWN="${1:-}"

# GAIA cores and their resource reservations
# Format: name:cpu_weight:memory_min_mb:memory_max_mb
CORES=(
    "guardian:1000:512:2048"      # Highest CPU weight, protected memory
    "nexus:900:512:4096"
    "terra:500:256:2048"
    "aqua:500:256:2048"
    "aero:500:256:2048"
    "vita:500:256:2048"
    "sophia:700:512:4096"
    "urbs:400:128:1024"
    "memory:600:1024:8192"        # Memory consolidation core
    "background:100:64:512"       # Lowest weight, elastic
)

teardown() {
    echo "[cgroups] Tearing down GAIA cgroup hierarchy..."
    for core_spec in "${CORES[@]}"; do
        name=$(echo "$core_spec" | cut -d: -f1)
        cg="$CGROUP_ROOT/$name"
        if [ -d "$cg" ]; then
            rmdir "$cg" 2>/dev/null || echo "  [warn] Could not remove $cg (tasks running?)"
        fi
    done
    rmdir "$CGROUP_ROOT" 2>/dev/null || true
    echo "[cgroups] Teardown complete."
}

setup() {
    echo "[cgroups] Setting up GAIA cgroup v2 hierarchy at $CGROUP_ROOT"

    # Ensure cgroup v2 is mounted
    if ! mountpoint -q /sys/fs/cgroup; then
        echo "ERROR: /sys/fs/cgroup is not mounted. Mount cgroup v2 first."
        exit 1
    fi

    mkdir -p "$CGROUP_ROOT"

    # Enable controllers for gaia cgroup
    echo "+cpu +memory +pids" > "$CGROUP_ROOT/cgroup.subtree_control" 2>/dev/null || \
        echo "  [warn] Could not enable all controllers (kernel may need CONFIG_MEMCG)"

    for core_spec in "${CORES[@]}"; do
        name=$(echo "$core_spec" | cut -d: -f1)
        cpu_weight=$(echo "$core_spec" | cut -d: -f2)
        mem_min_mb=$(echo "$core_spec" | cut -d: -f3)
        mem_max_mb=$(echo "$core_spec" | cut -d: -f4)

        cg="$CGROUP_ROOT/$name"
        mkdir -p "$cg"

        # CPU weight (1-10000, default 100)
        echo "$cpu_weight" > "$cg/cpu.weight" 2>/dev/null || true

        # Memory minimum (guaranteed reservation, bytes)
        mem_min_bytes=$(( mem_min_mb * 1024 * 1024 ))
        echo "$mem_min_bytes" > "$cg/memory.min" 2>/dev/null || true

        # Memory maximum (hard limit, bytes)
        mem_max_bytes=$(( mem_max_mb * 1024 * 1024 ))
        echo "$mem_max_bytes" > "$cg/memory.max" 2>/dev/null || true

        echo "  [ok] $cg (cpu.weight=$cpu_weight, memory.min=${mem_min_mb}MB, memory.max=${mem_max_mb}MB)"
    done

    echo "[cgroups] GAIA cgroup hierarchy ready."
    echo "[cgroups] Assign GAIA core PIDs with:"
    echo "          echo <PID> > /sys/fs/cgroup/gaia/<core>/cgroup.procs"
}

if [ "$TEARDOWN" = "--teardown" ]; then
    teardown
else
    setup
fi

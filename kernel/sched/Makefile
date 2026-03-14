# SPDX-License-Identifier: GPL-2.0
#
# kernel/sched/Makefile
#
# Builds the GAIA sched_ext BPF object.
#
# Usage:
#   make                         # build vmlinux.h + gaia_scx.bpf.o
#   make BPF_CLANG=clang-17      # pin a specific clang version
#   make BPFTOOL=/usr/sbin/bpftool
#   make clean

BPF_CLANG ?= clang
BPFTOOL   ?= bpftool

# Architecture token consumed by vmlinux.h / BPF CO-RE helpers.
# Override for cross-compilation: make ARCH_TOKEN=arm64
ARCH_TOKEN ?= x86

BPF_CFLAGS := \
	-target bpf \
	-D__TARGET_ARCH_$(ARCH_TOKEN) \
	-g \
	-O2 \
	-I.

.PHONY: all clean

all: vmlinux.h gaia_scx.bpf.o

vmlinux.h:
	$(BPFTOOL) btf dump file /sys/kernel/btf/vmlinux format c > $@

gaia_scx.bpf.o: gaia_scx.bpf.c vmlinux.h
	$(BPF_CLANG) $(BPF_CFLAGS) -c gaia_scx.bpf.c -o $@

clean:
	rm -f vmlinux.h gaia_scx.bpf.o

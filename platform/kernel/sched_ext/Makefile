# scx_gaia Makefile
# Requires: clang >= 16, libbpf-dev, linux-headers

CLANG   ?= clang
CC      ?= gcc
BPFTOOL ?= bpftool

BPF_CFLAGS := -g -O2 -target bpf -D__TARGET_ARCH_x86 \
              -I/usr/include/$(shell uname -m)-linux-gnu \
              -I/usr/local/include

ALL := scx_gaia_userspace

.PHONY: all clean

all: scx_gaia.bpf.o scx_gaia.skel.h scx_gaia_userspace

scx_gaia.bpf.o: scx_gaia.bpf.c
	$(CLANG) $(BPF_CFLAGS) -c $< -o $@

scx_gaia.skel.h: scx_gaia.bpf.o
	$(BPFTOOL) gen skeleton $< > $@

scx_gaia_userspace: scx_gaia_userspace.c scx_gaia.skel.h
	$(CC) -O2 -o $@ $< -lbpf -lelf -lz

clean:
	rm -f scx_gaia.bpf.o scx_gaia.skel.h scx_gaia_userspace

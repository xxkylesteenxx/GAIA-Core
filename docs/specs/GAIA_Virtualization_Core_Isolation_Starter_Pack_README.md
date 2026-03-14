# GAIA Virtualization and Core Isolation Starter Pack

This pack provides a **research-grade starter scaffold** for the GAIA virtualization substrate.
It is designed to support isolation between high-value GAIA services / cores using a Rust-first VMM control plane, memory-region policy enforcement, and a secure IPC bus.

## Important Status Note

This is **not** a production hypervisor. It is a starter architecture and code scaffold intended to be integrated with:
- Linux KVM
- rust-vmm crates (`kvm-ioctls`, `kvm-bindings`, `vm-memory`)
- optional QEMU/QMP management
- platform attestation and measured boot

## Included Components

| Path | Description |
|------|-------------|
| `docs/specs/VIRT-MEM-IPC-SPEC-v1.0.md` | Normative spec |
| `Cargo.toml` | Workspace manifest |
| `src/vmm/` | Rust VMM skeleton |
| `src/memory_isolation/` | Memory policy layer |
| `src/ipc_bus/` | Authenticated IPC bus skeleton |
| `src/c_bridge/` | C ABI / QEMU bridge scaffold |
| `examples/launch_layout.toml` | Example domain launch layout |

## Intended Model

- **KVM** provides the stable virtualization ABI on Linux.
- **Rust** provides the primary implementation language for VMM control logic and IPC.
- Per-core isolation is enforced by separate VMs / sandboxes, separate memory mappings, and explicit policy-mediated IPC.
- **QEMU** is optional and used via QMP or a C bridge when device-model compatibility is needed.

## Build Status

The Rust code is scaffold-level and intentionally conservative. It illustrates structure and interfaces but requires real dependencies and platform integration to run.

```
cargo build   # compiles the workspace skeletons
```

---
*See `docs/specs/VIRT-MEM-IPC-SPEC-v1.0.md` for normative requirements.*

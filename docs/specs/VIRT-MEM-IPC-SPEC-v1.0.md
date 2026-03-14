# GAIA Virtualization, Memory Isolation, and Inter-Core IPC Spec
<!-- Version: 1.0 | Status: Normative -->

## 1. Purpose

This section defines the GAIA virtualization substrate used to isolate high-value GAIA services / cores from each other so that compromise, corruption, starvation, or undefined behavior in one domain does not propagate laterally into protected domains.

## 2. Architectural Posture

GAIA SHALL implement a Rust-first virtualization control plane over the Linux KVM interface.
GAIA MAY integrate with QEMU for device-model compatibility, machine emulation, and management-plane interoperability, but QEMU SHALL NOT be the sole trust boundary.

## 3. Normative Components

| # | Component | Responsibility |
|---|-----------|----------------|
| 1 | **Virtual Machine Monitor (VMM)** | VM lifecycle, vCPU assignment, memory-region registration, device policy, attested launch |
| 2 | **KVM interface layer** | Stable Linux virtualization ABI — VM creation, vCPU control, memory mappings |
| 3 | **Memory isolation layer** | Region-policy subsystem — maps, tracks, and verifies per-core guest memory boundaries |
| 4 | **Inter-core IPC bus** | Authenticated, authorized, auditable message-passing fabric for cross-core coordination |
| 5 | **Optional QEMU / QMP bridge** | Compatibility path for device models and operational tooling |

## 4. Isolation Model

GAIA protected domains SHALL be modeled as separate isolation domains rather than as mutable trust labels inside a single shared process.

Recommended implementation options:
- Separate VMs for strongly isolated domains
- Separate processes plus sandboxing for less-trusted device model components
- Explicit control sockets and capability-scoped IPC channels

## 5. Memory Requirements

- Every protected GAIA domain SHALL receive an explicitly declared memory map.
- No domain SHALL be granted arbitrary read/write access to another domain's memory.
- Shared-memory regions, if used, SHALL be opt-in, labeled, bounded, and accompanied by integrity and freshness protections.
- Launch-time memory layouts SHALL be recorded in audit logs.

## 6. IPC Requirements

- All IPC endpoints SHALL be authenticated.
- All IPC routes SHALL be policy checked.
- Message schemas SHOULD be typed and versioned.
- High-risk control messages SHALL be durable, auditable, and reject-by-default.
- The IPC fabric SHALL support explicit allowlists for producer/consumer relationships.

## 7. Safety Posture

The virtualization layer SHALL use names such as `protected domains`, `critical services`, or `core workloads` in normative engineering text. Metaphysical or anthropomorphic labels MAY exist at the product language layer, but the substrate SHALL remain implementable in standard systems terms.

## 8. Implementation Split

| Language | Responsibility |
|----------|----------------|
| **Rust** | VMM control plane, memory policy engine, IPC bus, attestation integration |
| **KVM ABI** | ioctl-based VM and vCPU control |
| **C (optional)** | QEMU bridge shims, low-level compatibility adapters, device-model integration |

## 9. Verification Requirements

GAIA SHALL verify:
- VM launch policy conformance
- vCPU-to-domain assignment
- Memory region registration and non-overlap
- IPC route authorization
- Audit log completeness for launch, reset, shutdown, and cross-domain control actions

## 10. Out of Scope (This Section)

- Full device-model implementation
- Guest OS design
- Production attestation server implementation
- Side-channel elimination guarantees

---

*Spec section: VIRT-MEM-IPC · Version 1.0 · Status: Normative*

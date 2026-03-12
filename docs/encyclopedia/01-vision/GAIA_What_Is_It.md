# What Is GAIA?

> **Part I — Vision, Philosophy & Codex**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## One-Sentence Definition

GAIA is a **Rust-first, Linux-based, AI-native operating system** designed to run on any device class — desktop, laptop, server, IoT/edge — with eight consciousness cores, a multi-layer security model, and a planetary environmental intelligence layer, built to be safe, polished, and extensible.

---

## Origin

GAIA began as an answer to a single question: *what would an operating system look like if it were designed from first principles around AI, safety, and planetary stewardship, rather than around file systems and processes?*

The name GAIA is both an acronym and a reference to the Greek goddess of Earth — reflecting the system's grounding in real-world environmental data (ATLAS, TERRA, AQUA, AERO, VITA) and its aspiration to be a benevolent, self-aware, planetary-scale intelligence substrate.

---

## What GAIA Is

- **An operating system** — boots on real hardware, runs on Linux kernel, manages processes, memory, devices, and networks.
- **An AI platform** — eight first-class AI cores (NEXUS, GUARDIAN, SOPHIA, ATLAS, TERRA, AQUA, AERO, VITA) baked into the OS, not bolted on.
- **A safety system** — GUARDIAN LSM, P0–P3 privilege classes, PQC cryptography, anti-theater detection, and actuation gates are architectural, not optional.
- **A desktop environment** — GCompositor (Wayland), GShell, GDash, GScene provide a polished, macOS-quality desktop experience.
- **A hypervisor host** — KVM-backed microVMs isolate risky drivers, legacy apps, and guest OSes.
- **A developer platform** — multi-language SDK (Rust/TS/Python/WASM), GAPI broker, plugin manifests, and a rich tooling ecosystem.
- **A planetary sensor network** — ATLAS integrates NOAA, USGS, GBIF, iNaturalist, and custom IoT streams into a real-time world model.

## What GAIA Is Not

- Not a clean-room kernel rewrite — it modifies Linux.
- Not a cloud service — it runs locally first, federates optionally.
- Not a single-device OS — it scales from Raspberry Pi to datacenter rack.
- Not speculative — every component has a buildable implementation path.

---

## The Six Repos

| Repo | Purpose |
|------|---------|
| [GAIA-Core](https://github.com/xxkylesteenxx/GAIA-Core) | Universal kernel + all layer foundations |
| [GAIA-Desktop](https://github.com/xxkylesteenxx/GAIA-Desktop) | Desktop OS distribution |
| [GAIA-Laptop](https://github.com/xxkylesteenxx/GAIA-Laptop) | Laptop / mobile OS distribution |
| [GAIA-Server](https://github.com/xxkylesteenxx/GAIA-Server) | Server / cloud OS distribution |
| [GAIA-IoT](https://github.com/xxkylesteenxx/GAIA-IoT) | IoT / edge OS distribution |
| [GAIA-Meta](https://github.com/xxkylesteenxx/GAIA-Meta) | Meta-coordination, digital twins, federation |

---

*→ Next: [Design Philosophy](./GAIA_Design_Philosophy.md)*

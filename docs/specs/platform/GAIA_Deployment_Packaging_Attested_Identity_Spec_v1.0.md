# GAIA Deployment, Packaging, and Attested Identity Spec
**Version:** 1.0  
**Status:** Normative  
**Domain:** `platform/deployment`  
**Cross-refs:** GAIA-AI-INFERENCE-SPEC v1.0 | GUARDIAN v1.0 | GAIA Inter-Process Communication Spec v1.0 | GAIA Linux Kernel Modifications Spec v1.0

---

## 1. Purpose

This document defines the canonical deployment and identity-control substrate for GAIA server-side and fleet-side execution. It covers:

- container image construction;
- Kubernetes deployment and packaging;
- bare-metal bootstrap automation;
- reusable CI/CD workflow extension across GAIA repositories; and
- SPIRE/TPM-rooted node identity patterns.

---

## 2. Scope and Boundary Conditions

This section is a **starter implementation scaffold**. It is not a production release manifest set. It establishes architecture, file layout, config contracts, and secure defaults.

This spec intentionally excludes:
- high-risk destructive host imaging steps (see §7);
- live secret material storage in chart values (see §6);
- production admission control policies (see §12 follow-on).

---

## 3. Normative Design Principles

| ID | Principle | Keyword |
|---|---|---|
| DEP-001 | Container images SHALL be built from reproducible Dockerfiles and version-pinned dependencies where feasible | SHALL |
| DEP-002 | Helm charts SHALL package the same resource model as raw Kubernetes manifests | SHALL |
| DEP-003 | Fleet bootstrap SHOULD be driven by idempotent Ansible playbooks | SHOULD |
| DEP-004 | Repository-local workflows SHOULD call shared reusable workflows rather than duplicating job logic | SHOULD |
| DEP-005 | A node SHALL NOT be treated as a GAIA node solely because it presents network reachability | SHALL NOT |
| DEP-006 | Node identity MUST be bound to an attestation flow | MUST |
| DEP-007 | SPIRE issues workload identities; hardware trust still depends on the attestation root and validation policy | Informative |

---

## 4. Container Build Model

GAIA core containers SHOULD use:
- **multi-stage builds** — build-time toolchains SHALL NOT be left in runtime layers unless operationally required;
- **non-root runtime users** — the runtime process SHALL run as a non-root UID;
- **explicit health checks** where meaningful;
- **minimal runtime base image** — prefer distroless or slim variants.

### 4.1 Python Service Dockerfile Pattern

```dockerfile
# Stage 1 — build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2 — runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN useradd --system --uid 1001 gaia
USER gaia
HEALTHCHECK --interval=30s --timeout=5s CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
ENTRYPOINT ["python", "-m", "gaia_server"]
```

### 4.2 Rust Service Dockerfile Pattern

```dockerfile
# Stage 1 — build
FROM rust:1.77-slim AS builder
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release --locked

# Stage 2 — runtime (distroless)
FROM gcr.io/distroless/cc-debian12
COPY --from=builder /build/target/release/gaia_service /gaia_service
USER nonroot
ENTRYPOINT ["/gaia_service"]
```

---

## 5. Kubernetes Model

| Workload type | Resource | Rationale |
|---|---|---|
| Stateless APIs, routers, coordination | `Deployment` | Horizontal scaling, rolling updates |
| Stable network identity or persistent volumes | `StatefulSet` | Ordered pod identity, stable DNS |
| Configuration | `ConfigMap` | Externalized, version-controlled |
| Secrets | `Secret` | Externalized; injected by operator or sealed-secrets |

### 5.1 Network Policy Default

Inter-core network policy SHALL default to **deny** and allow only declared channels. Example base policy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: gaia-default-deny
  namespace: gaia
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

### 5.2 Overlay Model

Production overlays SHOULD express environment-specific replica counts, images, and policy values without rewriting the base object model. Use Kustomize `patches` or Helm `values.yaml` overrides — never fork base manifests per environment.

---

## 6. Helm Packaging Model

- The Helm chart SHALL template the same canonical Kubernetes resources used by the raw manifests.
- `values.yaml` SHALL be the primary release configuration surface.
- Secrets SHOULD be injected externally (sealed-secret, Vault operator, external-secrets-operator) or by a Kubernetes operator mechanism.
- Live secret material SHALL NOT be stored in chart values or committed to version control.

### 6.1 Canonical Chart Layout

```
helm/gaia-server/
  Chart.yaml
  values.yaml
  templates/
    deployment.yaml
    service.yaml
    configmap.yaml
    networkpolicy.yaml
    serviceaccount.yaml
    _helpers.tpl
```

---

## 7. Fleet Automation Model

Ansible SHALL manage:
- host bootstrap and package installation;
- container runtime installation;
- GAIA node directory layout;
- local configuration placement.

High-risk destructive host imaging steps are **intentionally excluded** from this starter pack. Playbooks target post-install bootstrap and idempotent convergence only.

### 7.1 Canonical Ansible Layout

```
ansible/
  inventory/
    hosts.yml
  roles/
    gaia_node/
      tasks/main.yml
      handlers/main.yml
      defaults/main.yml
      templates/
  playbooks/
    bootstrap.yml
    converge.yml
```

---

## 8. CI/CD Model

Shared reusable workflows SHALL provide:
- lint and syntax validation;
- container build steps;
- artifact packaging;
- optional publish gates;
- environment-aware deploy gates.

Repository-local callers SHOULD pass role-specific inputs and inherit secrets explicitly. Job logic SHALL NOT be duplicated across repository workflows (DEP-004).

### 8.1 Canonical Workflow Layout

```
.github/workflows/
  reusable-lint.yml       ← shared: YAML/Python/Rust lint
  reusable-build.yml      ← shared: container build + push
  reusable-deploy.yml     ← shared: environment-gated deploy
  ci.yml                  ← repo-local caller
```

### 8.2 Caller Pattern

```yaml
jobs:
  lint:
    uses: xxkylesteenxx/GAIA-Core/.github/workflows/reusable-lint.yml@main
    with:
      language: python
  build:
    needs: lint
    uses: xxkylesteenxx/GAIA-Core/.github/workflows/reusable-build.yml@main
    with:
      image: gaia-server
      dockerfile: docker/python/Dockerfile
    secrets: inherit
```

---

## 9. Attested Identity Model

SPIRE performs node attestation and workload attestation. A node SHALL NOT be trusted solely on network reachability (DEP-005); identity MUST be bound to an attestation flow (DEP-006).

| Deployment context | Attestation method |
|---|---|
| Kubernetes cluster nodes | PSAT (Projected Service Account Token) node attestor |
| Bare-metal / edge nodes | TPM-backed node attestation plugin (where hardware available) |
| Development / CI | Join token (short-lived, non-production only) |

### 9.1 SPIRE Responsibility Boundary

SPIRE issues **workload SVIDs** (X.509 or JWT). It is an identity plane, not the entire trust plane (DEP-007). Hardware trust depends on:
- TPM endorsement key validity;
- attestation policy configured in the SPIRE server;
- measured-boot verification (production follow-on, §12).

### 9.2 Canonical SPIRE Layout

```
spire/
  server/
    server.conf       ← SPIRE server config (trust domain, attestors, datastore)
  agent/
    agent.conf        ← SPIRE agent config (server address, join mechanism)
  enrollment/
    register_workload.sh   ← spire-server entry register scaffold
    register_node.sh       ← node attestation enrollment scaffold
```

---

## 10. Canonical File Families

```
docker/
  python/Dockerfile
  rust/Dockerfile
k8s/
  base/
    deployment.yaml
    service.yaml
    configmap.yaml
    networkpolicy.yaml
  overlays/
    dev/
    staging/
    production/
helm/gaia-server/         (see §6.1)
ansible/                  (see §7.1)
.github/workflows/        (see §8.1)
spire/                    (see §9.2)
```

---

## 11. Verification Requirements

The deployment pack SHALL support at minimum:

| Check | Tool |
|---|---|
| Kubernetes YAML parsing | `kubectl apply --dry-run=client` or `kubeconform` |
| Helm values parsing | `helm lint` + `helm template` |
| Ansible syntax | `ansible-playbook --syntax-check` |
| GitHub workflow YAML | `actionlint` |
| Bootstrap script syntax | `bash -n` / `shellcheck` |
| SPIRE config structure | Static review + `spire-server validate` |

---

## 12. Production Hardening Follow-On

Before production use, GAIA SHOULD add:

- [ ] Image signing and provenance (Sigstore / cosign)
- [ ] Admission control policies (Kyverno or OPA/Gatekeeper)
- [ ] Secret-manager integration (Vault, AWS Secrets Manager, or external-secrets-operator)
- [ ] SBOM generation (Syft / CycloneDX)
- [ ] TPM endorsement / attestation policy review
- [ ] Measured-boot verification policy
- [ ] Cluster-wide policy enforcement and runtime security telemetry (Falco)

---

## 13. Revision History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0 | 2026-03-14 | GAIA Core | Initial normative release |

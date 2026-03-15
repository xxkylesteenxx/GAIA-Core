# GAIA Deployment and Attested Identity Pack

This pack provides a repo-ready starter scaffold for:
- Dockerfiles for core service images
- Kubernetes manifests for GAIA-Server scale deployment
- Helm chart packaging for the Kubernetes release model
- Ansible playbooks for fleet bootstrap and node convergence
- GitHub Actions reusable workflow patterns and repository callers
- SPIRE/TPM-oriented example configuration and bootstrap scripts

## Layout

```
src/platform/deployment/
  docker/         — common Dockerfiles (Python, Rust)
  k8s/            — raw manifests and Kustomize overlays
  helm/           — Helm chart for gaia-server
  ansible/        — inventory, roles, playbooks
  github/         — reusable and caller GitHub Actions workflows
  spire/          — SPIRE server/agent config and enrollment scripts
  README.md       — this file
```

## Validation

- YAML files were parsed successfully in the build environment.
- Shell scripts passed `bash -n` syntax checks.
- Archive packaging completed successfully.

## Important boundary

This pack is a **secure starter scaffold**, not a finished production deployment.
Real secrets, cluster endpoints, TPM plugin binaries, and signing material must be
supplied by the deployment environment.

See `docs/specs/platform/GAIA_Deployment_Packaging_Attested_Identity_Spec_v1.0.md`
for the normative specification (DEP-001 – DEP-007).

## Production hardening checklist

Before production use, complete the items in spec §12:

- [ ] Image signing and provenance (Sigstore / cosign)
- [ ] Admission control policies (Kyverno or OPA/Gatekeeper)
- [ ] Secret-manager integration (Vault, external-secrets-operator)
- [ ] SBOM generation (Syft / CycloneDX)
- [ ] TPM endorsement / attestation policy review
- [ ] Measured-boot verification policy
- [ ] Runtime security telemetry (Falco)

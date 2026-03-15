# Contributing to GAIA-Core

Thank you for contributing to GAIA. This document covers the contribution
workflow, code standards, and review expectations.

## Getting Started

1. **Fork** the repository and create a feature branch from `main`:
   ```
   git checkout -b feat/your-feature-name
   ```
2. **Install** development dependencies:
   ```
   pip install -e ".[dev]"
   ```
3. **Run** the test suite before opening a PR:
   ```
   pytest tests/ -v
   ```

## Branch Naming

| Prefix | Use case |
|---|---|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `chore/` | Maintenance, dependencies, CI |
| `docs/` | Documentation only |
| `refactor/` | Code restructure without behaviour change |
| `test/` | Test additions or fixes |

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(storage): add semantic index projection query
fix(bootstrap): preserve backward-compat identity path
docs(specs): update dual-plane storage spec v1.1
```

## Pull Request Requirements

- All CI checks must pass (lint, type-check, tests)
- New code requires corresponding tests
- Public API changes require docstring updates
- Architecture-level changes require an ADR in `docs/adr/`
- Security-relevant changes require a SECURITY.md note if applicable

## Code Style

- Python: `ruff` for linting, `mypy` for type checking (see `pyproject.toml`)
- Rust: `rustfmt` + `clippy`
- Maximum line length: 100 characters
- All public functions and classes must have docstrings

## Architecture Decision Records

For decisions with lasting architectural impact, add an ADR:
```
docs/adr/ADR-NNNN-short-title.md
```
Use the template at `docs/adr/ADR-INDEX.md`.

## Code of Conduct

All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree your contributions are licensed under the
[Apache 2.0 License](../LICENSE).

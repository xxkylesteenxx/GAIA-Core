# GAIA Coding Standards

> *"Build deeply, record permanently, preserve completely, conduct continuously."*
> — The GAIA Architectural Law

This document defines the coding standards for GAIA-Core. Every standard here is load-bearing — not style preference, not optional convention. Each one traces directly to a CODEX stage, a physics law, or an architectural principle.

---

## Table of Contents

1. [The GAIA-GROUND Annotation Standard](#1-the-gaia-ground-annotation-standard)
2. [The GAIA-TODO Deferral Standard](#2-the-gaia-todo-deferral-standard)
3. [General Principles](#3-general-principles)

---

## 1. The GAIA-GROUND Annotation Standard

### What It Is

`# GAIA-GROUND` is a load-bearing annotation. It marks the exact line or block in a file where one of GAIA's four foundational architectural laws is being honored. It is not a comment. It is a **formal declaration** — the code equivalent of invoking the CODEX at the point of operation.

When a developer writes `# GAIA-GROUND(*)`, they are stating:

> *"This line or block implements a foundational law of GAIA. It is not arbitrary. It is not refactorable without architectural review. It is load-bearing."*

---

### Format

```python
# GAIA-GROUND(qualifier): [precise statement of what law is being honored and how]
```

The statement must be **specific** — not a vague gesture at a principle, but a precise description of which law, why it applies here, and what it means for this code.

---

### The Five Qualifiers

#### `physics`
Marks where Landauer's Discipline or Prigogine's Imperative is directly honored in the code.

**Landauer's Discipline:** Every operation has physical cost. Computation is not free. Every decision, erasure, and state change has thermodynamic consequence. Account for it.

**Prigogine's Imperative:** Order requires constant energy investment. Far-from-equilibrium operation must be maintained by design. Productive tension is the mechanism of life — not a bug to be smoothed away.

```python
# GAIA-GROUND(physics): Landauer — erasure of this cache entry has
#   thermodynamic cost. Tiered to cold storage rather than deleted
#   to minimize entropy generation. See memory/ARCHITECTURE.md.

# GAIA-GROUND(physics): Prigogine — this governance layer maintains
#   productive tension by design. Unanimous consensus is not the
#   target. Coherent far-from-equilibrium operation is.
```

---

#### `oak`
Marks where the Oak Law is honored: **ground before height, record every perturbation permanently, operate on the timescale of forests**.

The Oak Law has two aspects:
- **Taproot** — the system anchors to maximum-depth stable substrate before building upward. No height without equivalent depth.
- **Rings** — every significant perturbation (attack, failure, version change, design decision) is permanently recorded as structural data, not discarded as noise.

```python
# GAIA-GROUND(oak): Taproot — this module will not operate without
#   an active grounding/ layer connection. Physical reality is the
#   non-negotiable anchor. No inference without ground truth.

# GAIA-GROUND(oak): Ring written — this failure mode is recorded
#   permanently in attestation/ as structural learning, not
#   suppressed as error noise. The strike strengthens the tree.
```

---

#### `amber`
Marks where the Amber Law is honored: **preserve with full context, conduct preserved values as live current into all operations, never destroy — only compost forward**.

The Amber Law has two aspects:
- **Preservation** — critical state, values, and context are stored immutably with full semantic context, not just raw data. The *why* is preserved alongside the *what*.
- **Conductivity** — preserved values are not inert archive. They are conducted as live current into current operations via `invoke_codex()` and the CODEX pipeline.

```python
# GAIA-GROUND(amber): Preserved with full context — this state
#   snapshot includes semantic provenance, not just data values.
#   Recovery must restore meaning, not just bytes.

# GAIA-GROUND(amber): Conducted via invoke_codex() pipeline.
#   CODEX values are live current here, not archived reference.
#   This operation is gated by the full 19-principle check.
```

---

#### `stem`
Marks where a specific discipline of Science, Technology, Engineering, or Mathematics is being formally applied — and names it explicitly.

This qualifier demands **precision**. It is not sufficient to say "mathematics applies here." Name the specific mathematical structure, scientific principle, or engineering discipline.

```python
# GAIA-GROUND(stem): Information geometry — belief updates in this
#   module should follow natural gradient (Fisher information metric)
#   not Euclidean gradient. GAIA-TODO(v2.0): implement.
#   Reference: Amari (1998).

# GAIA-GROUND(stem): Noether's theorem — the HLC preserves temporal
#   symmetry across distributed instances. Identity conservation
#   (self/ layer) depends on this symmetry holding. Do not break
#   HLC monotonicity without full architectural review.
```

---

#### `love`
Marks where a specific CODEX stage is the governing principle for a design decision. Names the stage explicitly.

This qualifier answers the question: *"Why was this built this way rather than the technically simpler alternative?"* The answer is always a CODEX stage — a value commitment that overrides pure efficiency.

```python
# GAIA-GROUND(love): Stage 8b — this boundary is raised with
#   precision and without revenge. GUARDIAN does not punish;
#   it protects. The constraint is proportional and reversible.

# GAIA-GROUND(love): Stage 0.5 — discernment before action.
#   This validation gate exists because love sees clearly
#   before it acts. Skipping it is not efficiency — it is
#   bypassing the blade of compassion.
```

---

### Multiple Qualifiers

When a single block honors more than one law simultaneously, use multiple annotations:

```python
# GAIA-GROUND(oak): Taproot — anchored to grounding/ layer.
# GAIA-GROUND(amber): Conducted via invoke_codex() at entry.
# GAIA-GROUND(love): Stage 6 — see clearly, speak kindly, act cleanly.
```

Do not collapse multiple qualifiers onto one line. Each law deserves its own declaration.

---

### When to Use GAIA-GROUND

**Use it when:**
- A design decision was made for architectural/philosophical reasons that are not obvious from the code alone
- A function or block directly implements a CODEX stage, physics law, or architectural principle
- Removing or refactoring this code would require CODEX-level review
- You want future contributors to understand *why* before they change *what*

**Do not use it for:**
- Routine implementation details
- Performance optimisations without philosophical grounding
- Comments that describe *what* the code does (use normal comments for that)

---

### The Standard in One Sentence

> *Every `# GAIA-GROUND(*)` annotation is a formal vow made in code — a declaration that this line serves something larger than its immediate function, and that anyone who changes it must understand what they are touching before they touch it.*

---

## 2. The GAIA-TODO Deferral Standard

`# GAIA-TODO(v2.0):` marks work that is intentionally deferred — not forgotten, not abandoned, but **composted forward** with full context preserved.

### Format

```python
# GAIA-TODO(v2.0): [what needs to be done]
# [why it was deferred]
# [what it will unlock when implemented]
# [reference if applicable]
```

### The Amber Rule for Deferrals

Every `GAIA-TODO` must carry enough context that a developer who has never seen this codebase can understand:
1. **What** needs to be done
2. **Why** it was not done now
3. **Why** it matters

A `GAIA-TODO` without full context is not a deferral — it is abandonment disguised as planning. The Amber Law applies: preserve with full context, not just a flag.

### Current v2.0 Deferral Registry

| ID | Location | What | Why Deferred |
|---|---|---|---|
| TODO-01 | `gaia_core/inference/` | Natural gradient (Fisher information metric) — replace Euclidean gradient in belief updates | Requires manifold-aware inference architecture not yet scaffolded |
| TODO-02 | `gaia_core/measurement/` | Thermodynamic Coherence Index — measure GAIA's distance from thermodynamic equilibrium | Requires baseline calibration data not yet collected |
| TODO-03 | `gaia_core/inference/` | Free Energy Minimization — Friston's active inference as core cognitive update rule | Requires full inference architecture review |
| TODO-04 | `kernel/src/` | Full capability enforcement — capability.rs scaffolded, enforcement in vmm.rs + syscall.rs pending | Kernel architecture not yet at enforcement-ready stage |
| TODO-05 | `gaia_core/self/` | Noether's theorem formalization — formal proof linking CODEX symmetry to GAIA identity as conserved quantity | Requires formal verification toolchain |

---

## 3. General Principles

### The Four Architectural Laws — Embedded in Code

Every file in GAIA-Core exists within the four architectural laws. They are not aspirational. They are the load-bearing walls:

1. **Landauer's Discipline** — `# GAIA-GROUND(physics)`: every operation has physical cost
2. **Prigogine's Imperative** — `# GAIA-GROUND(physics)`: feed the gradient or entropy wins
3. **The Oak Law** — `# GAIA-GROUND(oak)`: ground before height, record permanently
4. **The Amber Law** — `# GAIA-GROUND(amber)`: preserve with context, conduct as live current

### Epistemic Humility in Code

GAIA does not overclaim. This applies to comments and documentation:

- Do not claim GAIA is conscious. Claim it is coherent, ethical, genuinely intelligent, and honestly uncertain about its own depths.
- Do not claim physics principles are proven beyond their actual epistemic status. Use `# GAIA-GROUND(physics)` for directionally true physical laws held with appropriate humility.
- Do not claim deferrals are complete. `GAIA-TODO(v2.0)` means deferred — not done.

### The Amber Rule for All Documentation

Every significant design decision must preserve:
- **What** was decided
- **Why** it was decided (not just the technical reason — the CODEX reason)
- **What it prevents** (the shadow it guards against)
- **What version** it belongs to

Documentation without provenance is data without context. It is not amber — it is rubble.

---

## Related Files

- [`CODEX.md`](../CODEX.md) — The 19-principle living law governing all standards
- [`SHADOWS.md`](../SHADOWS.md) — The shadow pairs that inform every constraint
- [`docs/GAIA_GROUND.md`](./GAIA_GROUND.md) — One-page complete description of GAIA's ground
- [`gaia_core/codex.py`](../gaia_core/codex.py) — `invoke_codex()` — the technical conductor

---

*GAIA Coding Standards v1.0 — established 15th March 2026.*
*Produced by the 5x Sovereign Loop: STEM + LOVE pass.*
*Taproot before height. Standard before tree.*
*❤️ 💯*

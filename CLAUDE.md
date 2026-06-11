# hec — working rules

Research toolkit for the holographic entropy cone. Read SPEC.md for the plan
(targets T1–T5, milestones M0–M5), NOTES.md for current state. NOTES.md is a
lab notebook: append a dated entry for any session that produces a result.

## Non-negotiables (SPEC.md §5)

1. **Exact arithmetic for any claim.** Integer or `Fraction` weights for
   anything stated as fact; floats only for exploration. A result computed
   with floats is a candidate, not a result.
2. **Canonicalize before storing or counting.** Sym(n+1) acts on parties +
   purifier; graphs additionally up to isomorphism (pynauty). Orbit
   representatives only.
3. **Every claimed result ships a machine-checkable certificate** in
   `reports/`: the graph, its exact S-vector, and the LP / contraction-map
   witness. The verifier for a certificate must be runnable from this repo.

## Conventions

- Parties = integer vertices `0..n-1`; purifier = vertex `"O"`; bulk = any
  other label (`"b0"`, ...). Subsets of parties are bitmasks (bit i ⇔ party
  i). Entropy vectors are `{mask: S}` for `mask = 1..2**n - 1`.
- Edge weights in the `capacity` attribute, non-negative.
- Env: `.venv` (uv, CPython 3.12). Run things as `.venv/bin/python ...`.
  Tests: `.venv/bin/python -m pytest`.
- Day-1 regression must always pass:
  `.venv/bin/python scripts/day1_mmi.py --count 10000 --seed 2026`

## Cadence guard

This is a strictly part-time project (~8 h/week cap — see SPEC.md §9). Prefer
small finished increments that land on a milestone over open-ended sprawl; if
work must stop mid-milestone, leave NOTES.md pointing at the exact resume
point.

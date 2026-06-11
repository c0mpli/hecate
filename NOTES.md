# Lab notebook

Newest entries first. Every claim here must be reproducible from a command in
this repo.

## 2026-06-12 — Session 2: M1 + M2 complete, P2 + P3 reproduced, M3 scaffolded

**M1 acceptance.** `verify_engine.py`: 1,000,000 random graphs (igraph fast
path, 6 workers), zero SA/AL/SSA/WM/MMI violations, 39.8 s. Fast path is
exact for integer weights (sums ≪ 2⁵³) and cross-validated against the
networkx reference on 360 graphs at n=3,4,5.

**P2 — the 5-party cone (arXiv:1903.09148), reproduced exactly** from
transcribed Tables 1–2 (`verify_c5.py`):
- 8 inequality orbits expand under purified Sym(6) to exactly the paper's
  sizes (15,20,45,72,10,60,60,90) → 372 facet instances.
- All 19 ray representatives satisfy all 372 instances and are extreme
  (saturated-facet rank 30 = dim−1, exact sympy).
- 19 distinct orbits, sizes summing to exactly 2267.
- `--duality`: Normaliz (exact double description, 19 min) re-derives the
  ray set from the 372 facets — equals the 19-orbit expansion **exactly**.

**M2 — contraction-map prover** (`prove_inequalities.py`, certificates in
`reports/contraction_maps/`):
- MMI re-derived by brute force in 0.5 s (the P1 deliverable); CP-SAT agrees.
- CP-SAT proves MMI2, QCyclic, Q2, Q4, Q5 (full all-pairs verification).
- Q3: CP-SAT returns INFEASIBLE on the *weighted* cube — a small theorem:
  Q3 has no weighted-cube contraction map; its proof needs the unit-expanded
  cube (3·S(ABC) → three coordinates), i.e. exactly the hard case that
  motivated the deterministic algorithm of arXiv:2403.13283. Next prover
  milestone: unit expansion (+ symmetry reduction over repeated coordinates).
- Canonicalization (`canon.py`): Sym(n+1) lex-min vector keys; weighted-graph
  keys via pynauty (edge-subdivision encoding, boundary vertices pinned).

**P3 — He–Hubeny–Rota classification (arXiv:2412.15364), re-verified from
scratch** (`verify_er6.py`, 208 rays from the paper's GitHub data repo,
mirrored in `data/raw/rota/`):
- All 208 are extreme rays of the 6-party subadditivity cone (saturated-SA
  rank 62; the SAC needs ALL polychromatic SA instances — 903 of them — not
  just the 21 atomic ones; bug caught by rank ceiling at 21) and all are
  SSA-compatible (3003 instances).
- HEI classification: checking all Sym(7) images (5040 index-permutations,
  numpy) against the 1877 Czech et al. orbit representatives gives exactly
  **52 violators / 156 clean — matching the paper**. (Representatives alone
  give 30 — orbit expansion is essential.)
- The 6 mystery orbits s ∈ {110, 145, 146, 168, 180, 181} confirmed clean →
  written with provenance to `data/targets/mystery_orbits.json`. These are
  the T1 targets.

**M3 scaffold** (`realize.py` v1: hill-climb over tree-biased topologies +
star/double-star motifs, integer weights, exact double verification):
- Independently realized 8/19 five-party orbits (all 7 star rays + ray 9)
  with certificates in `reports/realizations/` — found without looking at
  the paper's published graphs.
- Bounded first pass on the 6 mystery orbits (200 restarts × 3000 moves
  each): no realization — logged in `reports/mystery_attempts.jsonl`, no
  claim implied. The real attack is the (topology, cut-assignment) → LP
  feasibility engine of SPEC.md §6, which also yields exclusion certificates.

**Corrections to SPEC.md numbers:** Czech ancillary has **1877** inequalities
(not 1876); the data lives in M. Rota's GitHub repo (Zenodo DOI
10.5281/zenodo.14983856) — the arXiv v3 source tarball has no anc/ files.

**Next session:** LP cut-assignment realizer (trees first, per the tree
conjecture); unit-expanded Q3 proof; parse the 19 published C5 graphs
(data/raw/1903.09148/01..19.pdf) to cross-check the realizer; then sustained
mystery-orbit runs with exclusion bookkeeping.

## 2026-06-12 — Day 1: engine built and verified

**Done (full Day-1 checklist from SPEC.md):**

- All 9 reading-list papers fetched (`scripts/fetch_papers.sh`), plus ancillary
  data. The spec's arXiv IDs and claims all check out — the He–Hubeny–Rota
  abstract confirms: 208 genuine 6-party orbits, 52 non-holographic, 150
  realized by graphs (148 trees, 2 with a bulk cycle), **6 "mystery" orbits
  open**. Those 6 are the T1 targets.
- `entropy_vector(G, n)`: graph → S-vector via min-cut (networkx, super-
  source/sink reduction, uncapacitated edges = infinite). Integer weights
  throughout ⇒ every entropy exact.
- `check_vector(S, n)`: all SA / AL / SSA / WM / MMI instances over disjoint
  party subsets.
- Hand-computed ground truth (M0 acceptance): star graphs with bulk center
  (`S(A)=min(a, b+c+o)` etc.) and an all-boundary 4-cycle that *saturates*
  MMI (20 = 20). Both match the engine — `tests/test_entropy.py`.
- **The Day-1 assertion: 10,000 random graphs (stars / random trees with 0–4
  bulk vertices / trees + extra edges ⇒ bulk cycles), integer weights, seed
  2026 → zero violations of any inequality, exact arithmetic, 15.9 s.**
  Bonus: 500 graphs at n=4 and 200 at n=5 — also zero violations.
  Reproduce: `.venv/bin/python scripts/day1_mmi.py --count 10000 --seed 2026`

**Why the assertion *must* pass (checklist item 5):** for min-cut entropies,
MMI has a proof by cut-and-paste: given the minimal cuts for AB, AC, BC, their
union-and-intersection rearrangement produces candidate cuts for A, B, C, ABC
whose total weight is no larger (each edge is counted at least as many times
on the left as the right). Quantum states have no such mechanism — entropy of
a generic state is not a min-cut of anything. Live demo of the asymmetry:

```
>>> ghz = {m: 1 for m in range(1, 8)}   # 4-qubit GHZ: every bipartition has S=1
>>> check_vector(ghz, 3)
[('MMI', 1, 2, 4, -1)]                  # S(AB)+S(AC)+S(BC)=3 < 4=S(A)+S(B)+S(C)+S(ABC)
```

GHZ entanglement is quantum-legal but **cannot be geometry** — no weighted
graph, hence no smooth spacetime region, ever produces that vector. The HEC
facets are exactly these laws separating geometric from merely-quantum
entanglement. Day 1 verified one of them (MMI) from both sides.

**Data inventory:**

- `data/raw/2309.06296/anc/HEIforms.txt` + `HEIvectors.txt` — 1,876 known
  holographic entropy inequalities; vectors are 63 tab-separated integer
  coefficients per line (n=6 subset ordering to be confirmed against the
  paper), forms are Mathematica-style subset lists. P3 input.
- `data/raw/2412.15364/` — paper source only; **no machine-readable ancillary
  files**. The 208 orbit S-vectors (and the 6 mystery orbits) are in the .tex
  tables/figures — extraction + cross-check against the paper is a P3 task.

**Environment** (macOS, uv-managed CPython 3.12 in `.venv`): networkx 3.6.1,
python-igraph 1.0.0, numpy 2.4.6, sympy 1.14.0, ortools, pycddlib 3.0.2
(needs `brew install cddlib gmp`), pynauty 2.8.8.1 (needs `brew install
nauty`, build with `CFLAGS="-I$(brew --prefix)/include -I$(brew --prefix)/include/nauty"`),
Normaliz 3.11.1 (no brew formula — official binary unzipped to
`~/.local/opt/normaliz-3.11.1`, symlinked into `~/.local/bin`).

**Next (M0→M1):** read N&C ch. 2 + Preskill ch. 10 alongside BNOSSW §2–3;
then the igraph fast path + 10⁶-graph run, and encode the 19 five-party
extreme-ray orbits from arXiv:1903.09148 in exact arithmetic.

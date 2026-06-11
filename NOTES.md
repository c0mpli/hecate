# Lab notebook

Newest entries first. Every claim here must be reproducible from a command in
this repo.

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

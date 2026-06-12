# HECATE — Holographic Entropy Cone Analysis & Theorem Engine

[![CI](https://github.com/c0mpli/hecate/actions/workflows/ci.yml/badge.svg)](https://github.com/c0mpli/hecate/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Named for the goddess of boundaries and crossroads — fitting for an engine
that maps the boundary of which entanglement patterns can be geometry.

The holographic entropy cone reduces to graph combinatorics (BNOSSW,
arXiv:1505.07839): an entropy vector is holographic iff some weighted graph
realizes it via min-cuts. This repo builds the engine, the verifiers, and
the search loops to attack the open n=6 frontier. Full plan:
[SPEC.md](SPEC.md). The Python package keeps the short import name `hec`.

## Status

| Milestone | State |
|-----------|-------|
| M0 prereqs + env | **done** — engine hand-verified on star/cycle graphs |
| M1 engine + cone tools | **done** — 10⁶ graphs zero violations (40s); 5-party cone (P2) reproduced exactly incl. Normaliz facet↔ray duality (2267 rays) |
| M2 prover + canonicalization | **done** — MMI re-derived; CP-SAT proves 5/6 nontrivial C5 orbits (Q3: map requires the unit-expanded cube — pending, via arXiv:2403.13283) |
| P3 reproduction | **done** — all 208 six-party orbits re-verified (extreme rank-62, SSA-compatible); 52-violator index set == the paper's published list |
| C5 ground truth | **done** — all 19 published graph models transcribed & exactly verified (`hec/c5_graphs.py`); **19/19 ray realizations certified** in `reports/realizations/`: 16 fully independent (13 LP-cold + 3 annealed), 3 second-tier on published topologies (rays 10, 12, 19); derived split-tree oracles for 8/10 non-chordal rays |
| M3 the hunt | **reframed by the field** — {146, 180, 181} were realized via RL search in arXiv:2601.19979 (our independent verification: queued, next session); {110, 145, 168} remain open with non-realizability conjectured. All six fail the chordality gate: no simple-forest model exists for any of them (theorem, arXiv:2512.24490). The campaign on the suspects is two-track: (A) realization search over non-simple trees and cyclic graphs (slack-guided topology annealing), and (B) a separating-inequality hunt; absence-of-realization from annealing is never treated as evidence — exclusion claims come only from exclusion-grade machinery (bounded exhaustion of chordal fine-grainings) |

## Layout

- `hec/entropy.py` — graph → S-vector via min-cut (networkx exact path; igraph fast path, exact for integer weights)
- `hec/inequalities.py` — SA / AL / SSA / WM / MMI checks on entropy vectors
- `hec/graphs.py` — random graph generators (stars, trees, bulk cycles)
- `hec/subsets.py` — bitmask ↔ (size, lex) paper-order bookkeeping
- `hec/cone.py` — Sym(n+1) purified symmetry action, orbits, SA/SSA instance families, exact extremality
- `hec/prover.py` — contraction maps: checker, brute force, CP-SAT search
- `hec/canon.py` — dedupe keys: Sym(n+1) vector canon + pynauty weighted-graph canon
- `hec/realize.py` — target ray → graph search (v1 hill-climb)
- `hec/lp_realize.py` — LP cut-assignment engine: slack-LP descent → hard-pin constraint generation → exact integer certification
- `hec/anneal.py` — topology annealing with LP slack as fitness (the Sparse Oracle Principle: search sparse structure space, not dense supergraphs)
- `hec/chordality.py` — the arXiv:2512.24490 iff-gate for simple-forest realizability (correlation hypergraph → line graph → chordal); calibrated on all 19 C5 rays
- `hec/tree_builder.py` — Algorithm 1 of arXiv:2512.18702: constructive simple-tree builder, 9/9 exact on the chordal C5 rays
- `hec/c5_graphs.py` — the 19 published C5 graph models, transcribed and exactly verified
- `hec/splits.py` + `entropy_vector_labeled` — non-simple models (multi-vertex parties); boundary-splitting transform with exact re-verification
- `hec/n6er_data.py` — the two public tree-resistant n=6 models (verified; not SAC-extreme, ranks 58/61)
- `hec/c5_data.py`, `hec/hei_data.py` — arXiv:1903.09148 tables; arXiv:2309.06296 loader
- `scripts/` — `day1_mmi`, `verify_engine` (10⁶ run), `verify_c5` (P2 + `--duality`), `verify_hei6`, `verify_er6` (P3 + target extraction), `prove_inequalities`, `prove_q3_expanded`, `realize_c5` / `attempt_mystery` (`--engine lp|hill`), `fetch_papers.sh`
- `data/targets/mystery_orbits.json` — the 6 open T1 targets, validated, with provenance
- `reports/` — machine-checkable certificates (contraction maps, realizations)
- `NOTES.md` — running lab notebook

Pending: party-splitting moves for the annealer (non-simple tree search),
the Bao–Naskar deterministic prover (arXiv:2403.13283; the Q3 unit-expanded
proof waits on it), chordal fine-graining exclusion machinery (campaign
track B), `falsify.py`, `search.py` evolutionary loop, `db.py` store.

## Setup & run

```sh
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python -e '.[dev]' sympy   # core
uv pip install -p .venv/bin/python '.[search]'         # igraph, ortools, numpy
./scripts/fetch_papers.sh                               # papers + ancillary data

.venv/bin/python -m pytest                              # ground-truth tests
.venv/bin/python scripts/day1_mmi.py --count 10000      # the Day-1 assertion
```

## Data & references

Results in this repo are computed against, and verified to reproduce, the
following sources:

- **arXiv:1505.07839** (Bao–Nezami–Ooguri–Stoica–Sully–Walter) — the graph-model
  theorem and contraction-map proof method this entire toolkit is built on.
- **arXiv:1903.09148** (Hernández Cuenca) — the 5-party cone; Tables 1–2
  transcribed in `hec/c5_data.py` and re-verified here (372 facets ↔ 2,267
  extreme rays, including an independent Normaliz double-description run).
- **arXiv:2309.06296** (Czech–Dong–Hernández Cuenca et al.) — the 1,877 known
  6-party holographic entropy inequalities; loaded from the paper's arXiv
  ancillary files (`HEIvectors.txt`).
- **arXiv:2412.15364** (He–Hubeny–Rota) — the 208 SSA-compatible extreme-ray
  orbits of the 6-party subadditivity cone; full classification re-verified
  here. Ray data from the authors' repository
  [Max-Rota/SSA-compatible-Extreme-Rays-of-the-Subadditivity-Cone](https://github.com/Max-Rota/SSA-compatible-Extreme-Rays-of-the-Subadditivity-Cone)
  (DOI: 10.5281/zenodo.14983856), **pinned at commit `e973df6e0aa6`** —
  `scripts/fetch_papers.sh` clones exactly that snapshot.
- Methods arc for the prover: arXiv:2403.13283 → 2409.17317 → 2506.18086
  (contraction-map algorithmics and completeness).
- **arXiv:2204.00075** (Hernández Cuenca–Hubeny–Rota) — the tree conjecture,
  the fig. N5trees non-simple trees, and the entropy-preserving graph
  operations; source of the two tree-resistant n=6 models verified in
  `hec/n6er_data.py`.
- **arXiv:2412.18018** (Hubeny–Rota) — the correlation hypergraph and the
  original chordality necessary condition.
- **arXiv:2512.18702** (Hubeny–Rota) — the constructive simple-tree
  algorithm (our `hec/tree_builder.py`) and the fine-graining toolkit.
- **arXiv:2512.24490** (Hubeny–Rota) — chordality is necessary AND
  sufficient (the iff-gate in `hec/chordality.py`).
- **arXiv:2601.19979** (He–Lee–Ooguri) — RL realization of mystery orbits
  {146, 180, 181}; code at
  [Jaeha0526/EntropyCone_RL](https://github.com/Jaeha0526/EntropyCone_RL).
  Our independent verification of their graphs is queued; their data will be
  pinned at a specific commit when pulled.

The distilled T1 targets (`data/targets/mystery_orbits.json`) ship in-repo
with provenance and validation steps recorded in the file itself.

## Conventions

Parties are integer vertices `0..n-1`, the purifier is vertex `"O"`, subsets
of parties are bitmasks (bit i ⇔ party i), entropy vectors are
`{mask: S(mask)}` for `mask = 1..2ⁿ−1`. Edge weights live in the `capacity`
attribute and are integers unless a claim needs `Fraction`s — floats explore,
they never prove (SPEC.md §5, rule 1).

# HECATE — Holographic Entropy Cone Analysis & Theorem Engine

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
| M2 prover + canonicalization | **done** — MMI re-derived; CP-SAT proves 5/6 nontrivial C5 orbits; Q3: weighted-cube map proven impossible, expanded-cube search needs the 2403.13283 algorithm (next) |
| P3 reproduction | **done** — all 208 six-party orbits re-verified (extreme rank-62, SSA-compatible); 52-violator index set == the paper's published list |
| M3 the hunt | **engine live** — 6 mystery targets extracted & validated (`data/targets/`); LP cut-assignment realizer independently realizes **13/19** C5 rays with exact certificates; mystery runs logged in `reports/` |

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
- `hec/c5_data.py`, `hec/hei_data.py` — arXiv:1903.09148 tables; arXiv:2309.06296 loader
- `scripts/` — `day1_mmi`, `verify_engine` (10⁶ run), `verify_c5` (P2 + `--duality`), `verify_hei6`, `verify_er6` (P3 + target extraction), `prove_inequalities`, `prove_q3_expanded`, `realize_c5` / `attempt_mystery` (`--engine lp|hill`), `fetch_papers.sh`
- `data/targets/mystery_orbits.json` — the 6 open T1 targets, validated, with provenance
- `reports/` — machine-checkable certificates (contraction maps, realizations)
- `NOTES.md` — running lab notebook

Pending per SPEC.md: LP (topology, cut-assignment) realizer, Bao–Naskar
deterministic prover (2403.13283), Q3 unit-expanded proof, `falsify.py`,
`search.py` evolutionary loop, `db.py` store.

## Setup & run

```sh
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python -e '.[dev]' sympy   # core
uv pip install -p .venv/bin/python '.[search]'         # igraph, ortools, numpy
./scripts/fetch_papers.sh                               # papers + ancillary data

.venv/bin/python -m pytest                              # ground-truth tests
.venv/bin/python scripts/day1_mmi.py --count 10000      # the Day-1 assertion
```

## Conventions

Parties are integer vertices `0..n-1`, the purifier is vertex `"O"`, subsets
of parties are bitmasks (bit i ⇔ party i), entropy vectors are
`{mask: S(mask)}` for `mask = 1..2ⁿ−1`. Edge weights live in the `capacity`
attribute and are integers unless a claim needs `Fraction`s — floats explore,
they never prove (SPEC.md §5, rule 1).

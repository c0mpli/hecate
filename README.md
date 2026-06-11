# hec — holographic entropy cone toolkit

Mapping which patterns of entanglement can be geometry. The holographic
entropy cone reduces to graph combinatorics (BNOSSW, arXiv:1505.07839):
an entropy vector is holographic iff some weighted graph realizes it via
min-cuts. This repo builds the engine, the verifiers, and the search loops
to attack the open n=6 frontier. Full plan: [SPEC.md](SPEC.md).

## Status

| Milestone | State |
|-----------|-------|
| M0 prereqs + env | **done** (Day 1) — engine hand-verified on star/cycle graphs |
| M1 entropy engine + cone tools | engine done & verified (10⁴ graphs, exact, zero violations; n=3,4,5); cone tools pending |
| M2 prover + canonicalization | pending |
| M3 the hunt (6 open orbits of arXiv:2412.15364) | pending |

## Layout

- `hec/entropy.py` — graph → S-vector via min-cut (integer/exact by default)
- `hec/inequalities.py` — SA / AL / SSA / WM / MMI checks on entropy vectors
- `hec/graphs.py` — random graph generators (stars, trees, bulk cycles)
- `scripts/day1_mmi.py` — N random graphs, assert all inequalities hold
- `scripts/fetch_papers.sh` — reading list + ancillary data (the manifest for `papers/`, `data/raw/`)
- `tests/` — hand-computed ground-truth S-vectors
- `NOTES.md` — running lab notebook

Pending modules per SPEC.md §5: `cone.py`, `prover.py`, `realize.py`,
`falsify.py`, `search.py`, `db.py`.

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

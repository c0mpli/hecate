#!/usr/bin/env python3
"""P3 reproduction: re-verify the He-Hubeny-Rota classification (2412.15364).

Input: the 208 genuine 6-party SSA-compatible extreme-ray orbit
representatives (data/raw/rota/n6_rays.txt, from the paper's data repo).

From scratch, in exact integer arithmetic, this checks for every ray:
  (a) it lies in the 6-party subadditivity cone (every SA/AL instance >= 0),
  (b) it is SSA-compatible (every SSA/WM instance >= 0),
  (c) it is an *extreme* ray of the SA cone (saturated SA instances have
      rank 62 = dim - 1),
  (d) its violation count against the 1877 known holographic entropy
      inequalities (arXiv:2309.06296).

Expected (paper): 208/208 pass (a)-(c); exactly 52 orbits violate >= 1 HEI;
the 156 non-violators include the 6 "mystery" orbits s in {110, 145, 146,
168, 180, 181} (1-indexed rows). On success, writes the 6 mystery vectors
with provenance to data/targets/mystery_orbits.json.
"""

import json
import multiprocessing as mp
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
MYSTERY = [110, 145, 146, 168, 180, 181]  # 1-indexed (paper's s labels)

_ctx = {}


def _init():
    from hec.cone import sa_instances, ssa_instances
    from hec.hei_data import load_hei6

    _ctx["SA"] = sa_instances(6)    # all 903 SA/AL facets of the 6-party SAC
    _ctx["SSA"] = ssa_instances(6)  # all polychromatic SSA/WM instances
    _ctx["HEI"] = load_hei6()


def _check(task):
    import sympy

    idx, ray = task
    SA, SSA = _ctx["SA"], _ctx["SSA"]
    dots_sa = [sum(a * b for a, b in zip(f, ray)) for f in SA]
    in_sa = all(d >= 0 for d in dots_sa)
    ssa_ok = all(sum(a * b for a, b in zip(f, ray)) >= 0 for f in SSA)
    sat = [f for f, d in zip(SA, dots_sa) if d == 0]
    rank = sympy.Matrix(sat).rank() if sat else 0
    return idx, in_sa, ssa_ok, rank


def main():
    rays = [
        tuple(int(x) for x in line.split())
        for line in (ROOT / "data/raw/rota/n6_rays.txt").read_text().strip().splitlines()
    ]
    assert len(rays) == 208 and all(len(r) == 63 for r in rays)

    _init()
    print(f"SA-cone instances: {len(_ctx['SA'])}; SSA instances: {len(_ctx['SSA'])}; "
          f"known HEIs: {len(_ctx['HEI'])}")

    t0 = time.perf_counter()
    with mp.Pool(6, initializer=_init) as pool:
        results = pool.map(_check, list(enumerate(rays, start=1)))
    dt = time.perf_counter() - t0

    bad = []
    for idx, in_sa, ssa_ok, rank in sorted(results):
        if not (in_sa and ssa_ok and rank == 62):
            bad.append((idx, in_sa, ssa_ok, rank))
    if bad:
        print("FAIL: rays not SSA-compatible-extreme:", bad)
        sys.exit(1)
    print(f"[a-c] OK: all 208 rays are extreme rays of the SA cone (rank 62) "
          f"and SSA-compatible ({dt:.1f}s)")

    # (d) violation against ALL instances of the 1877 known HEI orbits:
    # check every Sym(7) image of each ray against the representatives
    # (f . (pi r) >= 0 for all pi  <=>  (pi^-1 f) . r >= 0 for all pi).
    import numpy as np

    from hec.cone import perm_index_matrix

    t1 = time.perf_counter()
    PERM = np.array(perm_index_matrix(6), dtype=np.intp)        # 5040 x 63
    H = np.array(_ctx["HEI"], dtype=np.int64).T                 # 63 x 1877
    violators, clean = [], []
    for idx, ray in enumerate(rays, start=1):
        imgs = np.array(ray, dtype=np.int64)[PERM]              # 5040 x 63
        (violators if (imgs @ H < 0).any() else clean).append(idx)
    print(f"[d] HEI violators (all instances): {len(violators)} orbits; "
          f"clean: {len(clean)} ({time.perf_counter() - t1:.1f}s)")
    assert len(violators) == 52, f"paper says 52 violators, got {len(violators)}"
    missing = [s for s in MYSTERY if s not in clean]
    assert not missing, f"mystery orbits violating HEIs?! {missing}"
    print(f"    52 violators / 156 clean — matches the paper exactly")
    print(f"    mystery rows {MYSTERY} all violate zero known HEIs — confirmed")

    out = ROOT / "data" / "targets"
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "what": "the 6 unresolved ('mystery') extreme-ray orbits at n=6 — T1 targets",
        "source": "arXiv:2412.15364 (He-Hubeny-Rota); vectors from the paper's "
                  "data repo github.com/Max-Rota/SSA-compatible-Extreme-Rays-of-"
                  "the-Subadditivity-Cone, n=6/rays.txt rows s (1-indexed)",
        "ordering": "63 components, subsets of {A..F} sorted by (size, lex); "
                    "last component = S(ABCDEF) = purifier entropy",
        "verified": "each is an extreme ray of the 6-party SA cone (saturated "
                    "rank 62), SSA-compatible, and violates none of the 1877 "
                    "known HEIs (arXiv:2309.06296) — rechecked exactly by "
                    "scripts/verify_er6.py",
        "orbits": {str(s): list(rays[s - 1]) for s in MYSTERY},
    }
    path = out / "mystery_orbits.json"
    path.write_text(json.dumps(payload, indent=2))
    print(f"T1 targets written to {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

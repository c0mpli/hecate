#!/usr/bin/env python3
"""Prove Q3 (arXiv:1903.09148 Table 1, row 6) by contraction on the
unit-expanded cube.

The weighted-cube search is INFEASIBLE for Q3 (proven by CP-SAT earlier), so
the proof must live on the expanded cube: 3*S(ABC) becomes three unit
coordinates, giving L=16, R=18. Searching all maps is hopeless (2^16 domain);
we search copy-symmetric maps in the count representation (8192 classes),
where a solution lifts canonically to a genuine contraction map.

A found map is re-verified independently (boundary anchors + every class
adjacency) and additionally swept over all 2^16 * 16 / 2 actual hypercube
edges as a belt-and-braces check before the certificate is written.
"""

import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hec.c5_data import C5_INEQUALITIES
from hec.prover import (
    Inequality,
    check_symmetric_expanded,
    find_contraction_symmetric_expanded,
)

OUT = pathlib.Path(__file__).resolve().parent.parent / "reports" / "contraction_maps"


def full_edge_sweep(ineq, cmap):
    """Check the canonical lift is edge-Lipschitz on the real 2^L cube."""
    Lg = [(m, c) for c, m in ineq.lhs]
    coord_group = []
    for g, (_, mult) in enumerate(Lg):
        coord_group += [g] * mult
    L = len(coord_group)
    n_groups = len(Lg)

    def cls(x):
        counts = [0] * n_groups
        for j in range(L):
            if x >> j & 1:
                counts[coord_group[j]] += 1
        return tuple(counts)

    bad = 0
    for x in range(1 << L):
        cx = cmap[cls(x)]
        for j in range(L):
            if not x >> j & 1:
                cy = cmap[cls(x | (1 << j))]
                if sum(abs(a - b) for a, b in zip(cx, cy)) > 1:
                    bad += 1
    return bad


def main():
    name, lhs, rhs = [q for q in C5_INEQUALITIES if q[0] == "Q3"][0]
    q3 = Inequality(name, lhs, rhs, 5)
    print(f"Q3 expanded: L = {sum(q3.alpha)} unit coords in {q3.L} groups, "
          f"R = {sum(q3.beta)} in {q3.R} groups; "
          f"{4**3 * 2**7} domain classes")

    t0 = time.perf_counter()
    cmap = find_contraction_symmetric_expanded(q3, time_limit_s=1500, workers=6)
    dt = time.perf_counter() - t0
    status = find_contraction_symmetric_expanded.last_status
    print(f"CP-SAT: {status} in {dt:.1f}s")
    if cmap is None:
        if status == "INFEASIBLE":
            print("No copy-symmetric expanded map exists — asymmetric maps "
                  "not excluded; needs the 2403.13283 deterministic search.")
        sys.exit(2)

    errs = check_symmetric_expanded(q3, cmap)
    assert not errs, errs[:5]
    t1 = time.perf_counter()
    bad = full_edge_sweep(q3, cmap)
    assert bad == 0, f"{bad} bad hypercube edges"
    print(f"verified: class adjacencies + boundary anchors + full sweep of "
          f"all 2^16 x 16 hypercube edge slots ({time.perf_counter()-t1:.1f}s)")

    OUT.mkdir(parents=True, exist_ok=True)
    cert = {
        "inequality": repr(q3),
        "name": "Q3",
        "method": "contraction map on the unit-expanded cube, copy-symmetric "
                  "(count representation), found by CP-SAT",
        "lhs_groups": [[m, c] for c, m in q3.lhs],
        "rhs_groups": [[m, c] for c, m in q3.rhs],
        "seconds": round(dt, 1),
        "note": "weighted-cube contraction map proven INFEASIBLE; this is the "
                "expanded-cube proof. Verify with "
                "hec.prover.check_symmetric_expanded.",
        "class_map": {" ".join(map(str, k)): " ".join(map(str, v))
                      for k, v in sorted(cmap.items())},
    }
    path = OUT / "Q3_expanded.json"
    path.write_text(json.dumps(cert, indent=2))
    print(f"Q3 PROVEN — certificate: {path.name} "
          f"({len(cmap)} classes)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""P2 reproduction: the 5-party holographic entropy cone (arXiv:1903.09148).

Exact, from-scratch verification of the paper's central claims using only
the transcribed Tables 1-2:

 1. The 8 inequality orbits have sizes (15,20,45,72,10,60,60,90) -> 372
    distinct facet instances.
 2. The 19 ray representatives lie in the cone the 372 facets cut out.
 3. Each is an extreme ray (saturated facets have rank 30 = dim - 1).
 4. The 19 rays lie in 19 *distinct* Sym(6) orbits whose sizes sum to 2267.
 5. (--duality) Re-derive all extreme rays from the 372 facets with Normaliz
    (exact double description) and check the set equals the union of the 19
    orbits — full facet<->ray duality, independently recomputed.
"""

import argparse
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hec.c5_data import (
    C5_EXTREME_RAYS,
    C5_INEQUALITIES,
    EXPECTED_FACET_ORBIT_SIZES,
    TOTAL_EXTREME_RAYS,
    TOTAL_FACETS,
)
from hec.cone import (
    canonical_vector,
    expand_inequalities,
    in_cone,
    is_extreme_ray,
    orbit,
)
from hec.subsets import paper_order, vector_from_paper

N = 5
WORK = pathlib.Path(__file__).resolve().parent.parent / "reports" / "c5_duality"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duality", action="store_true", help="run Normaliz cross-check")
    args = ap.parse_args()

    t0 = time.perf_counter()
    facets, sizes = expand_inequalities(C5_INEQUALITIES, N)
    names = [q[0] for q in C5_INEQUALITIES]
    print("facet orbit sizes:", dict(zip(names, sizes)))
    assert sizes == EXPECTED_FACET_ORBIT_SIZES, "orbit sizes disagree with paper"
    assert len(facets) == TOTAL_FACETS, f"expected 372 facets, got {len(facets)}"
    print(f"[1] OK: 8 orbits -> {len(facets)} distinct facet instances")

    rays = [vector_from_paper(r, N) for r in C5_EXTREME_RAYS]
    ray_tuples = list(C5_EXTREME_RAYS)
    assert all(in_cone(r, facets) for r in ray_tuples)
    print("[2] OK: all 19 ray representatives satisfy all 372 inequalities")

    for k, r in enumerate(ray_tuples, 1):
        assert is_extreme_ray(r, facets, N), f"ray {k} is not extreme"
    print("[3] OK: all 19 rays are extreme (saturated-facet rank = 30)")

    orbits = [orbit(r, N) for r in rays]
    reps = {canonical_vector(r, N) for r in rays}
    assert len(reps) == 19, "ray representatives are not in 19 distinct orbits"
    total = sum(len(o) for o in orbits)
    print(f"ray orbit sizes: {[len(o) for o in orbits]}")
    assert total == TOTAL_EXTREME_RAYS, f"expected 2267 rays, got {total}"
    print(f"[4] OK: 19 distinct orbits, {total} extreme rays in total")
    print(f"core checks done in {time.perf_counter() - t0:.1f}s")

    if not args.duality:
        return

    # [5] independent re-derivation: facets -> rays via Normaliz
    WORK.mkdir(parents=True, exist_ok=True)
    infile = WORK / "c5.in"
    dim = len(paper_order(N))
    lines = [f"amb_space {dim}", f"inequalities {len(facets)}"]
    lines += [" ".join(str(c) for c in f) for f in facets]
    lines.append("ExtremeRays")
    infile.write_text("\n".join(lines) + "\n")
    t1 = time.perf_counter()
    subprocess.run(
        ["normaliz", "-x=6", str(infile)], check=True, capture_output=True, text=True
    )
    # parse the "<k> extreme rays:" block of the .out file (version-stable)
    rows = (WORK / "c5.out").read_text().splitlines()
    got = set()
    for i, line in enumerate(rows):
        if line.strip().endswith("extreme rays:"):
            k = int(line.split()[0])
            for r in rows[i + 1 : i + 1 + k]:
                got.add(tuple(int(x) for x in r.split()))
            break
    expected = set().union(*orbits)
    assert len(got) == TOTAL_EXTREME_RAYS, f"Normaliz found {len(got)} rays"
    assert got == expected, "Normaliz ray set differs from 19-orbit expansion"
    print(
        f"[5] OK: Normaliz double description reproduces exactly the same "
        f"{len(got)} extreme rays ({time.perf_counter() - t1:.1f}s)"
    )


if __name__ == "__main__":
    main()

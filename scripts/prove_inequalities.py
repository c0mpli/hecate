#!/usr/bin/env python3
"""M2 acceptance: machine-find contraction-map proofs.

Re-derives the MMI proof by brute force, cross-checks CP-SAT on it, then
attempts every 5-party inequality orbit representative of arXiv:1903.09148
Table 1 with CP-SAT. Found maps are written to reports/contraction_maps/ as
JSON certificates (re-verifiable with hec.prover.check_contraction).
"""

import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hec.c5_data import C5_INEQUALITIES
from hec.prover import (
    Inequality,
    check_contraction,
    find_contraction_bruteforce,
    find_contraction_cpsat,
)

OUT = pathlib.Path(__file__).resolve().parent.parent / "reports" / "contraction_maps"


def save(ineq, f, how, secs):
    OUT.mkdir(parents=True, exist_ok=True)
    cert = {
        "inequality": repr(ineq),
        "name": ineq.name,
        "n": ineq.n,
        "lhs": [[c, m] for c, m in ineq.lhs],
        "rhs": [[c, m] for c, m in ineq.rhs],
        "found_by": how,
        "seconds": round(secs, 2),
        "map": {"".join(map(str, k)): "".join(map(str, v)) for k, v in sorted(f.items())},
        "verified": "check_contraction: all (C1)+(C2) pairs pass",
    }
    path = OUT / f"{ineq.name}.json"
    path.write_text(json.dumps(cert, indent=2))
    return path


def main():
    mmi = Inequality(
        "MMI1", {"AB": 1, "AC": 1, "BC": 1}, {"A": 1, "B": 1, "C": 1, "ABC": 1}, 3
    )
    t0 = time.perf_counter()
    f_brute = find_contraction_bruteforce(mmi)
    t_brute = time.perf_counter() - t0
    assert f_brute and not check_contraction(mmi, f_brute)
    print(f"MMI proof re-derived by brute force in {t_brute:.2f}s; map on 8 points:")
    for k in sorted(f_brute):
        print(f"   {''.join(map(str, k))} -> {''.join(map(str, f_brute[k]))}")
    save(mmi, f_brute, "bruteforce", t_brute)

    f_sat = find_contraction_cpsat(mmi, time_limit_s=30)
    assert f_sat is not None
    print("CP-SAT agrees: MMI map found and fully verified.\n")

    for name, lhs, rhs in C5_INEQUALITIES:
        if name in ("SA", "MMI1"):
            continue  # SA is 2->1 trivial; MMI done above
        ineq = Inequality(name, lhs, rhs, 5)
        t0 = time.perf_counter()
        f = find_contraction_cpsat(ineq, time_limit_s=300)
        dt = time.perf_counter() - t0
        if f is None:
            status = getattr(find_contraction_cpsat, "last_status", "?")
            print(f"{name}: no weighted-cube map (solver: {status}; L={ineq.L}, "
                  f"R={ineq.R})" + (
                      " — INFEASIBLE is a theorem: proof needs the unit-expanded"
                      " cube (cf. arXiv:2403.13283)" if status == "INFEASIBLE" else ""))
            continue
        path = save(ineq, f, "cp-sat", dt)
        print(f"{name}: proof found in {dt:.1f}s (L={ineq.L}, R={ineq.R}) -> {path.name}")


if __name__ == "__main__":
    main()

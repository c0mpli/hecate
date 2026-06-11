#!/usr/bin/env python3
"""Day-1 acceptance run (SPEC.md checklist item 4).

Generates random weighted graphs with 3 parties + purifier, computes each
entropy vector by min-cut, and checks SA / AL / SSA / WM / MMI on every
vector. The graph model theorem (arXiv:1505.07839) says zero violations is
the only acceptable outcome — any hit is an engine bug and gets dumped as a
JSON certificate to reports/.

Usage: day1_mmi.py [--count 10000] [--n 3] [--seed 2026] [--wmax 64]
"""

import argparse
import json
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from hec.entropy import entropy_vector, subset_label
from hec.graphs import random_mixture
from hec.inequalities import check_vector, describe_violation

REPORTS = pathlib.Path(__file__).resolve().parent.parent / "reports"


def dump_violation(G, S, bad, n, seed, index):
    REPORTS.mkdir(exist_ok=True)
    cert = {
        "what": "inequality violation — ENGINE BUG, graph vectors must satisfy these",
        "seed": seed,
        "graph_index": index,
        "edges": [[str(u), str(v), d["capacity"]] for u, v, d in G.edges(data=True)],
        "entropy_vector": {subset_label(m, n): S[m] for m in sorted(S)},
        "violations": [describe_violation(v, n) for v in bad],
    }
    path = REPORTS / f"violation_seed{seed}_graph{index}.json"
    path.write_text(json.dumps(cert, indent=2))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10_000)
    ap.add_argument("--n", type=int, default=3, help="number of parties")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--wmax", type=int, default=64)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    checks = 0
    t0 = time.perf_counter()
    for i in range(args.count):
        G = random_mixture(args.n, rng, wmax=args.wmax)
        S = entropy_vector(G, args.n)
        bad = check_vector(S, args.n)
        if bad:
            path = dump_violation(G, S, bad, args.n, args.seed, i)
            print(f"VIOLATION on graph {i} — certificate at {path}")
            for v in bad:
                print("  " + describe_violation(v, args.n))
            sys.exit(1)
        checks += 1
        if checks % 2000 == 0:
            rate = checks / (time.perf_counter() - t0)
            print(f"  {checks}/{args.count} graphs, 0 violations ({rate:,.0f} graphs/s)")

    dt = time.perf_counter() - t0
    print(
        f"PASS: {args.count} random graphs (n={args.n}, seed={args.seed}), "
        f"all SA/AL/SSA/WM/MMI instances hold, exact integer arithmetic. "
        f"{dt:.1f}s ({args.count / dt:,.0f} graphs/s)"
    )


if __name__ == "__main__":
    main()

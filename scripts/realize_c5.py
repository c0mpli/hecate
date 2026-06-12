#!/usr/bin/env python3
"""Realizer validation: independently find graph models for the 19 five-party
extreme-ray orbit representatives (arXiv:1903.09148 Table 2).

The paper publishes one graph per orbit (as figures); we don't read those —
each hit here is an independent realization, exactly verified. Certificates
go to reports/realizations/.

Usage: realize_c5.py [--restarts 80] [--moves 2000] [--workers 6]
"""

import argparse
import json
import multiprocessing as mp
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

OUT = pathlib.Path(__file__).resolve().parent.parent / "reports" / "realizations"


def attempt(task):
    idx, ray, restarts, moves, seed, engine = task

    rng = random.Random(seed + idx)
    t0 = time.perf_counter()
    if engine == "lp":
        from hec.lp_realize import lp_realize_target

        hit = lp_realize_target(ray, 5, rng, attempts=restarts)
    else:
        from hec.realize import realize_target

        hit = realize_target(
            ray, 5, rng, scales=(1, 2), restarts=restarts, moves=moves,
            allow_cycles=True,
        )
    dt = time.perf_counter() - t0
    if hit is None:
        return idx, None, dt
    G, k = hit
    edges = [[str(u), str(v), d["capacity"]] for u, v, d in G.edges(data=True)]
    return idx, {"scale": k, "edges": edges}, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=80)
    ap.add_argument("--moves", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--engine", choices=["hill", "lp"], default="hill")
    ap.add_argument("--only", type=str, default="",
                    help="comma-separated ray indices (default: all 19)")
    args = ap.parse_args()

    from hec.c5_data import C5_EXTREME_RAYS

    only = {int(x) for x in args.only.split(",") if x} or set(range(1, 20))
    tasks = [
        (i, ray, args.restarts, args.moves, args.seed, args.engine)
        for i, ray in enumerate(C5_EXTREME_RAYS, start=1)
        if i in only
    ]
    with mp.Pool(args.workers) as pool:
        results = pool.map(attempt, tasks)

    OUT.mkdir(parents=True, exist_ok=True)
    found = []
    for idx, hit, dt in sorted(results):
        if hit is None:
            print(f"ray {idx:2d}: not found ({dt:.0f}s) — no claim, v1 heuristic only")
            continue
        found.append(idx)
        cert = {
            "what": f"graph model independently realizing 5-party extreme ray {idx}",
            "ray": list(C5_EXTREME_RAYS[idx - 1]),
            "ordering": "(size, lex), purifier = O vertex",
            "scale": hit["scale"],
            "edges": hit["edges"],
            "verify": "hec.entropy.entropy_vector(G, 5) == scale * ray",
        }
        (OUT / f"c5_ray{idx:02d}.json").write_text(json.dumps(cert, indent=2))
        print(f"ray {idx:2d}: REALIZED (scale {hit['scale']}, "
              f"{len(hit['edges'])} edges, {dt:.0f}s)")
    print(f"\n{len(found)}/19 orbits independently realized -> {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Topology-annealing run on C5 rays (the post-oracle capability fix).

Usage: anneal_c5.py [--only 10,12,16,17,18,19] [--rounds 4] [--iters 350]
                    [--workers 6] [--seed 2026]

Each round is an independent annealing trajectory; any hit is already
exact-certified by fit_weights. Certificates land in reports/realizations/
(marked engine=anneal).
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
    k, ray, rounds, iters, seed = task
    from hec.anneal import anneal_topology

    t0 = time.perf_counter()
    for r in range(rounds):
        rng = random.Random(seed * 1000 + 17 * k + r)
        hit = anneal_topology(ray, 5, rng, iters=iters)
        if hit:
            G, s = hit
            edges = [[str(u), str(v), d["capacity"]] for u, v, d in G.edges(data=True)]
            return k, {"scale": s, "edges": edges}, time.perf_counter() - t0
    return k, None, time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=str, default="10,12,16,17,18,19")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--iters", type=int, default=350)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    from hec.c5_data import C5_EXTREME_RAYS

    only = [int(x) for x in args.only.split(",") if x]
    tasks = [(k, C5_EXTREME_RAYS[k - 1], args.rounds, args.iters, args.seed)
             for k in only]
    with mp.Pool(min(args.workers, len(tasks))) as pool:
        results = pool.map(attempt, tasks)

    OUT.mkdir(parents=True, exist_ok=True)
    for k, hit, dt in sorted(results):
        if hit is None:
            print(f"ray {k:2d}: not found ({dt:.0f}s)")
            continue
        verts = {x for u, v, _ in hit["edges"] for x in (u, v)}
        cert = {
            "what": f"graph model independently realizing 5-party extreme ray {k}",
            "engine": "topology annealing + LP weight fit (hec.anneal)",
            "ray": list(C5_EXTREME_RAYS[k - 1]),
            "ordering": "(size, lex), purifier = O vertex",
            "scale": hit["scale"],
            "edges": hit["edges"],
            "cyclomatic": len(hit["edges"]) - len(verts) + 1,
            "verify": "hec.entropy.entropy_vector(G, 5) == scale * ray",
        }
        (OUT / f"c5_ray{k:02d}.json").write_text(json.dumps(cert, indent=2))
        print(f"ray {k:2d}: REALIZED ({len(hit['edges'])} edges, scale "
              f"{hit['scale']}, {dt:.0f}s) -> c5_ray{k:02d}.json")


if __name__ == "__main__":
    main()

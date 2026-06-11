#!/usr/bin/env python3
"""Engine verification at scale (M1 acceptance: 10^6 graphs, zero violations).

Multiprocess version of day1_mmi.py with a backend switch. Each worker draws
graphs from the Day-1 mixture with its own derived seed, computes S-vectors
(igraph fast path by default — exact for integer weights), and checks every
SA / AL / SSA / WM / MMI instance.

Usage: verify_engine.py [--count 1000000] [--n 3] [--seed 2026]
                        [--workers 6] [--backend igraph|networkx]
"""

import argparse
import multiprocessing as mp
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def worker(task):
    seed, count, n, wmax, backend = task
    # imports inside the worker: macOS uses spawn
    from hec.entropy import entropy_vector, entropy_vector_fast
    from hec.graphs import random_mixture
    from hec.inequalities import check_vector, describe_violation

    compute = entropy_vector_fast if backend == "igraph" else entropy_vector
    rng = random.Random(seed)
    for i in range(count):
        G = random_mixture(n, rng, wmax=wmax)
        S = compute(G, n)
        bad = check_vector(S, n)
        if bad:
            edges = [(str(u), str(v), d["capacity"]) for u, v, d in G.edges(data=True)]
            return {
                "violation": [describe_violation(v, n) for v in bad],
                "edges": edges,
                "seed": seed,
                "index": i,
            }
    return {"ok": count}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1_000_000)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--wmax", type=int, default=64)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--backend", choices=["igraph", "networkx"], default="igraph")
    args = ap.parse_args()

    per = args.count // args.workers
    counts = [per] * args.workers
    counts[0] += args.count - per * args.workers
    tasks = [
        (args.seed * 1000 + w, counts[w], args.n, args.wmax, args.backend)
        for w in range(args.workers)
    ]

    t0 = time.perf_counter()
    with mp.Pool(args.workers) as pool:
        results = pool.map(worker, tasks)
    dt = time.perf_counter() - t0

    total = 0
    for r in results:
        if "violation" in r:
            print(f"VIOLATION (worker seed {r['seed']}, graph {r['index']}):")
            for v in r["violation"]:
                print("  " + v)
            print("  edges:", r["edges"])
            sys.exit(1)
        total += r["ok"]

    print(
        f"PASS: {total:,} random graphs (n={args.n}, backend={args.backend}, "
        f"seed={args.seed}, workers={args.workers}), zero violations of "
        f"SA/AL/SSA/WM/MMI, integer-exact. {dt:.1f}s ({total / dt:,.0f} graphs/s)"
    )


if __name__ == "__main__":
    main()

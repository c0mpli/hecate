#!/usr/bin/env python3
"""Validate engine + Czech data at the n=6 frontier.

Random 6-party graphs -> 63-component S-vectors -> every one of the 1877
known holographic entropy inequalities (arXiv:2309.06296) must hold. This
simultaneously tests the entropy engine at n=6 and the loader's
ordering/sign conventions: a mistake in either produces violations within a
handful of graphs.

Usage: verify_hei6.py [--count 20000] [--workers 6] [--seed 2026]
"""

import argparse
import multiprocessing as mp
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def worker(task):
    seed, count, wmax = task
    import numpy as np

    from hec.entropy import entropy_vector_fast
    from hec.graphs import random_mixture
    from hec.hei_data import load_hei6
    from hec.subsets import vector_to_paper

    H = np.array(load_hei6(), dtype=np.int64)  # 1877 x 63
    rng = random.Random(seed)
    for i in range(count):
        G = random_mixture(6, rng, wmax=wmax)
        S = entropy_vector_fast(G, 6)
        s = np.array(vector_to_paper(S, 6), dtype=np.int64)
        vals = H @ s
        if (vals < 0).any():
            idx = [int(j) for j in (vals < 0).nonzero()[0]]
            edges = [(str(u), str(v), d["capacity"]) for u, v, d in G.edges(data=True)]
            return {"violation": idx, "edges": edges, "seed": seed, "index": i}
    return {"ok": count}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=20_000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--wmax", type=int, default=64)
    args = ap.parse_args()

    per = args.count // args.workers
    counts = [per] * args.workers
    counts[0] += args.count - per * args.workers
    tasks = [(args.seed * 77 + w, counts[w], args.wmax) for w in range(args.workers)]

    t0 = time.perf_counter()
    with mp.Pool(args.workers) as pool:
        results = pool.map(worker, tasks)
    dt = time.perf_counter() - t0

    total = 0
    for r in results:
        if "violation" in r:
            print(f"VIOLATION: inequalities {r['violation']} on graph {r['index']} "
                  f"(worker seed {r['seed']}); edges: {r['edges']}")
            sys.exit(1)
        total += r["ok"]
    print(
        f"PASS: {total:,} random 6-party graphs x 1877 known HEIs "
        f"({total * 1877:,} inequality evaluations), zero violations. "
        f"{dt:.1f}s ({total / dt:,.0f} graphs/s)"
    )


if __name__ == "__main__":
    main()

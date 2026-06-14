#!/usr/bin/env python3
"""Ladder rung 1: validate the party-splitting tree annealer on C5 rays 10-19.

These rays are non-chordal (no simple tree) but tree-realizable by NON-simple
trees (arXiv:2204.00075 fig. N5trees; we derived split-trees for 8/10 in
session 5). The annealer must rediscover non-simple trees from scratch before
it is trusted on the bulk-cycle pair {111, 207}. A pass = high hit-rate on
11-19; rays 10, 17 (bulk cycle survives boundary-splitting) are the stretch.

No claim about 111/207 may be made until this rung passes. Annealer FAILURE
here means the tool isn't ready — never that a ray is unrealizable.
"""

import argparse
import multiprocessing as mp
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx


def attempt(task):
    k, iters, restarts, seed = task
    from hec.c5_data import C5_EXTREME_RAYS
    from hec.entropy import entropy_vector_labeled
    from hec.subsets import vector_from_paper
    from hec.tree_search import anneal_tree

    t0 = time.perf_counter()
    res = anneal_tree(C5_EXTREME_RAYS[k - 1], 5, random.Random(seed + k),
                      iters=iters, restarts=restarts, probe_descents=12)
    dt = time.perf_counter() - t0
    if res is None:
        return k, None, dt
    G, scale, party = res
    S = entropy_vector_labeled(G, 5, party)
    tgt = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
    # a simple FOREST realization is acceptable (cf. arXiv:2512.24490);
    # acyclicity is what matters for the bulk-cycle question, not connectedness
    ok = all(S[m] == scale * tgt[m] for m in tgt) and nx.is_forest(G)
    nb = sum(1 for v in G if isinstance(v, str) and v.startswith("b"))
    return k, (ok, scale, len(party), nb), dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rays", type=str, default="10,11,12,13,14,15,16,17,18,19")
    ap.add_argument("--iters", type=int, default=500)
    ap.add_argument("--restarts", type=int, default=6)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    rays = [int(x) for x in args.rays.split(",")]
    tasks = [(k, args.iters, args.restarts, args.seed) for k in rays]
    with mp.Pool(min(args.workers, len(tasks))) as pool:
        results = pool.map(attempt, tasks)

    hits = 0
    for k, r, dt in sorted(results):
        if r is None:
            print(f"ray {k:2d}: not found ({dt:.0f}s)")
        else:
            ok, scale, leaves, nb = r
            hits += ok
            print(f"ray {k:2d}: {'TREE' if ok else 'BAD'} scale={scale} "
                  f"leaves={leaves} bulk={nb} ({dt:.0f}s)")
    print(f"\nrung-1: {hits}/{len(rays)} non-simple trees found")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""C5 ladder gate for hec/search.py — the binding validation before any
111/207 run (same discipline that correctly halted tree_search.py at 1/8).

Rays 10-19 are non-chordal (no simple tree) but tree-realizable by NON-simple
trees — KNOWN answers (8/10 settled by boundary-splitting in session 5; rays
10, 17 keep a bulk cycle after splitting and are the Δ-Y stretch). Each tree
found is exact-certified by the loop. Reports N/10.

A pass earns a run on the bulk-cycle pair. A miss on a ray is NOT evidence
that ray lacks a tree — it bounds only this loop's reach under this budget.
"""

import argparse
import multiprocessing as mp
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

VALID_DIR = pathlib.Path(__file__).resolve().parent.parent / "reports" / "realizations" / "c5_ladder_validation"


def attempt(task):
    k, iters, secs, seed = task
    from hec.c5_data import C5_EXTREME_RAYS
    from hec.search import POLICY, search

    pol = dict(POLICY)
    pol["budget_iters"] = iters
    pol["budget_seconds"] = secs
    pol["log_every"] = 10 ** 9  # quiet per-ray; summary only
    t0 = time.perf_counter()
    logs = []
    path = search(C5_EXTREME_RAYS[k - 1], 5, f"c5_{k}",
                  random.Random(seed + k), policy=pol,
                  log=lambda m: logs.append(m), out_dir=VALID_DIR)
    return k, (path is not None), time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rays", type=str, default="10,11,12,13,14,15,16,17,18,19")
    ap.add_argument("--iters", type=int, default=3000)
    ap.add_argument("--seconds", type=int, default=900)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    rays = [int(x) for x in args.rays.split(",")]
    tasks = [(k, args.iters, args.seconds, args.seed) for k in rays]
    with mp.Pool(min(args.workers, len(tasks))) as pool:
        results = pool.map(attempt, tasks)

    hits = 0
    for k, ok, dt in sorted(results):
        hits += ok
        print(f"ray {k:2d}: {'TREE FOUND' if ok else 'no tree (budget)'} ({dt:.0f}s)")
    print(f"\nLADDER: {hits}/{len(rays)} tree realizations found "
          f"(known-realizable rays; misses bound only this loop's reach)")


if __name__ == "__main__":
    main()

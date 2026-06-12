#!/usr/bin/env python3
"""First bounded attempt at the 6 mystery orbits (T1 targets).

v1 heuristic search only — a hit would be a result (and is verified exactly,
twice, before being written); a miss is logged coverage, NOT evidence of
impossibility. Exclusion certificates require the exhaustive
(topology, cut-assignment) LP engine, which is the M3 main line.

Usage: attempt_mystery.py [--restarts 200] [--moves 3000] [--workers 6]
"""

import argparse
import json
import multiprocessing as mp
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent


def attempt(task):
    s, vec, restarts, moves, seed, engine = task

    rng = random.Random(seed * 13 + s)
    t0 = time.perf_counter()
    if engine == "lp":
        from hec.lp_realize import lp_realize_target

        hit = lp_realize_target(tuple(vec), 6, rng, attempts=restarts)
    else:
        from hec.realize import realize_target

        hit = realize_target(
            tuple(vec), 6, rng,
            scales=(1, 2), bulk_range=(0, 7), restarts=restarts, moves=moves,
            allow_cycles=True,
        )
    dt = time.perf_counter() - t0
    if hit is None:
        return s, None, dt
    G, k = hit
    return s, {"scale": k, "edges": [[str(u), str(v), d["capacity"]] for u, v, d in G.edges(data=True)]}, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=200)
    ap.add_argument("--moves", type=int, default=3000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--engine", choices=["hill", "lp"], default="hill")
    args = ap.parse_args()

    targets = json.loads((ROOT / "data/targets/mystery_orbits.json").read_text())
    tasks = [
        (int(s), vec, args.restarts, args.moves, args.seed, args.engine)
        for s, vec in targets["orbits"].items()
    ]
    with mp.Pool(args.workers) as pool:
        results = pool.map(attempt, tasks)

    log = {"attempt": f"engine={args.engine}", "restarts": args.restarts,
           "moves": args.moves, "seed": args.seed, "results": {}}
    for s, hit, dt in sorted(results):
        if hit is None:
            print(f"orbit s={s}: no realization found ({dt:.0f}s) — coverage logged, no claim")
            log["results"][str(s)] = {"found": False, "seconds": round(dt)}
        else:
            print(f"orbit s={s}: !!! REALIZED !!! — verify and email per SPEC.md §8")
            log["results"][str(s)] = {"found": True, **hit}
            out = ROOT / "reports" / f"MYSTERY_s{s}_REALIZED.json"
            out.write_text(json.dumps({"s": s, "target": targets["orbits"][str(s)], **hit}, indent=2))
    path = ROOT / "reports" / "mystery_attempts.jsonl"
    path.parent.mkdir(exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(log) + "\n")
    print(f"attempt log appended to {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

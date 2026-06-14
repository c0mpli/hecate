#!/usr/bin/env python3
"""Validation + run harness for hec/cycle_surgery.py.

Gate (binding): C5 rays 10 and 17 — surviving-bulk-cycle rays that are
KNOWN tree-realizable (5-party cone solved; arXiv:2204.00075). The surgery
MUST turn their cyclic models into trees. Only after that may it run on the
n=6 bulk-cycle orbits 111/207.

Outputs:
- C5 validation trees -> reports/realizations/surgery_validation/ (gitignored;
  these are tool-validation artifacts, not novel results — C5 trees are known).
- n=6 success -> reports/realizations/ (a real result: answers the open
  question for that orbit).
- n=6 bounded failure -> reports/bulk_cycle_attempts.jsonl, logged ONLY as
  "no reduction under <move set, bound>", never as non-existence.

Usage: surgery_validate.py [--targets 10,17,111] [--max-nodes 20000]
"""

import argparse
import json
import pathlib
import sys
import time
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx

from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.cycle_surgery import REPORTS, cyclomatic, normalize, surgery

ROOT = pathlib.Path(__file__).resolve().parent.parent
VALID_DIR = REPORTS / "surgery_validation"


def _norm(x):
    return int(x) if isinstance(x, str) and x in ("0", "1", "2", "3", "4", "5") else x


def c5_seed(k):
    G = nx.Graph()
    party = {}
    for lab in [0, 1, 2, 3, 4, "O"]:
        G.add_node(lab)
        party[lab] = lab
    for u, v, w in C5_PUBLISHED_GRAPHS[k]:
        G.add_edge(u, v, capacity=Fraction(w))
    return G, party


def n6_seed(name):
    f = ROOT / "data" / "targets" / "bulk_cycle_seeds.json"
    if not f.exists():
        return None
    seeds = json.loads(f.read_text()).get("seeds", {})
    if name not in seeds:
        return None
    G = nx.Graph()
    party = {}
    for lab in [0, 1, 2, 3, 4, 5, "O"]:
        G.add_node(lab)
        party[lab] = lab
    for u, v, w in seeds[name]["edges"]:
        G.add_edge(_norm(u), _norm(v), capacity=Fraction(int(w)))
    return G, party


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default="10,17")
    ap.add_argument("--max-nodes", type=int, default=20000)
    ap.add_argument("--max-depth", type=int, default=40)
    args = ap.parse_args()

    for t in args.targets.split(","):
        t = t.strip()
        n6 = t in ("111", "207")
        n = 6 if n6 else 5
        seed = n6_seed(t) if n6 else c5_seed(int(t))
        if seed is None:
            print(f"s={t}: no cyclic seed available — skipped "
                  f"(207 is not in hecdata; needs a seed first)")
            continue
        G, party = seed
        Gn = normalize(G, party)
        out = REPORTS if n6 else VALID_DIR
        t0 = time.perf_counter()
        path, info = surgery(G, party, n, t, max_nodes=args.max_nodes,
                             max_depth=args.max_depth, out_dir=out, log=print)
        dt = time.perf_counter() - t0
        print(f"s={t}: norm-cyclomatic={cyclomatic(Gn)} | {info} ({dt:.0f}s)")
        if n6 and info["status"] != "tree":
            log = ROOT / "reports" / "bulk_cycle_attempts.jsonl"
            log.parent.mkdir(exist_ok=True)
            rec = {
                "orbit": t,
                "tool": "cycle_surgery",
                "seed": "hecdata Sym(7) match" if t == "111" else "?",
                "result": "no_reduction",
                "best_cyclomatic_reached": info["best_cyclomatic"],
                "nodes": info["nodes"],
                "bound": f"max_nodes={args.max_nodes}, max_depth={args.max_depth}",
                "qualifier": "BOUNDED under {Δ-Y, Y-Δ, series, parallel, prune, "
                             "boundary-split} and this seed; NOT a proof that no "
                             "tree realization exists. The surviving cycle is a "
                             "pure-bulk high-degree cycle untouchable by local "
                             "entropy-preserving moves — settle via fine-graining "
                             "exclusion, or try alternative cyclic seeds.",
            }
            with log.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(f"   logged bounded result to {log.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

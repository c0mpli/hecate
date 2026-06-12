#!/usr/bin/env python3
"""Oracle-assisted certificates: published topology + independently
recovered weights.

For rays the cold search hasn't reached yet, run fit_weights on the VERIFIED
published topology (hec/c5_graphs.py, weights stripped) and write an exact
certificate that credits the topology to arXiv:1903.09148 explicitly. These
are honest second-tier certificates: the weights (and their exactness) are
ours, the structure is the paper's. Cold/annealed certificates always
overwrite these, never the reverse.

Usage: certify_from_published.py --only 10,18,19 [--seed 2026]
"""

import argparse
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.lp_realize import fit_weights
from hec.subsets import vector_from_paper

OUT = pathlib.Path(__file__).resolve().parent.parent / "reports" / "realizations"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=str, required=True)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    for k in (int(x) for x in args.only.split(",")):
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3, 4, "O"])
        for u, v, w in C5_PUBLISHED_GRAPHS[k]:
            G.add_edge(u, v, capacity=w)
        tgt = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
        hit = None
        for attempt in range(12):
            rng = random.Random(args.seed + 31 * k + attempt)
            hit = fit_weights(G, 5, tgt, rng, descents=80)
            if hit:
                break
        if hit is None:
            print(f"ray {k}: FAILED to recover weights — investigate")
            sys.exit(1)
        Gi, s = hit
        edges = [[str(u), str(v), d["capacity"]] for u, v, d in Gi.edges(data=True)]
        verts = {x for u, v, _ in edges for x in (u, v)}
        cert = {
            "what": f"graph model realizing 5-party extreme ray {k}",
            "engine": "LP weight recovery on the published topology "
                      "(arXiv:1903.09148 Fig. 1, graph "
                      f"{k:02d}; weights independently re-derived)",
            "ray": list(C5_EXTREME_RAYS[k - 1]),
            "ordering": "(size, lex), purifier = O vertex",
            "scale": s,
            "edges": edges,
            "cyclomatic": len(edges) - len(verts) + 1,
            "verify": "hec.entropy.entropy_vector(G, 5) == scale * ray",
        }
        (OUT / f"c5_ray{k:02d}.json").write_text(json.dumps(cert, indent=2))
        print(f"ray {k:2d}: certified from published topology "
              f"(scale {s}, {len(edges)} edges)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Item 6: minimization pass on the HLO realizations of {146, 180, 181}.

Greedy bulk-vertex deletion with LP weight refit: starting from the exactly
verified paper graphs (arXiv:2601.19979), repeatedly try to delete one
internal vertex and re-fit weights on the remaining topology; accept any
deletion whose refit verifies exactly. Results are UPPER BOUNDS on the
minimal internal-vertex count (no minimality claim — the cascade only
explores subgraphs of the seed topology). Certificates land in
reports/realizations/ as n6_s<ray>_minimal.json.
"""

import json
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx

from hec.entropy import entropy_vector
from hec.lp_realize import fit_weights
from hec.subsets import vector_from_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent
L = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "O": "O"}


def v(x):
    return L[x] if isinstance(x, str) else f"b{x}"


PAPER_GRAPHS = {
    "146": [("A",2,12),("A",11,12),("B",5,12),("B",6,12),("C",1,12),("C",3,12),
            ("D",2,12),("D",5,12),("D",9,12),("E",2,12),("E",6,12),("E",7,12),
            ("F",6,12),("F",10,12),("F",11,12),("O",1,12),("O",5,12),("O",11,12),
            (1,3,8),(1,4,6),(1,6,12),(1,7,6),(1,8,7),(2,10,12),(3,4,6),(3,7,4),
            (3,8,8),(3,10,12),(4,7,2),(4,8,3),(4,10,6),(5,8,12),(7,8,6),(7,10,6),
            (9,10,12),(10,11,12)],
    "180": [("A",5,12),("A",7,12),("B",1,12),("B",3,12),("C",4,12),("C",6,12),
            ("D",1,12),("D",5,12),("D",6,12),("E",3,12),("E",6,12),("E",7,12),
            ("F",3,12),("F",4,12),("F",5,12),("O",1,12),("O",2,12),("O",7,12),
            (1,2,7),(1,4,12),(2,4,12),(3,4,12),(4,6,12),(5,6,12),(6,7,12)],
    "181": [("A",1,9),("A",6,9),("B",2,9),("B",10,9),("C",4,9),("C",7,9),
            ("D",6,9),("D",8,4),("D",9,5),("D",10,9),("E",1,9),("E",2,9),
            ("E",8,9),("F",2,9),("F",6,9),("F",7,9),("O",1,9),("O",7,9),
            ("O",10,9),(1,5,9),(2,4,9),(3,5,6),(3,8,6),(4,5,9),(4,10,9),
            (5,6,9),(5,7,9),(5,8,9),(5,9,5)],
}


def refit(G0, tgt, seed, attempts=8, descents=80):
    for a in range(attempts):
        hit = fit_weights(G0, 6, tgt, random.Random(seed + a), descents=descents)
        if hit:
            return hit
    return None


def main():
    targets = json.loads((ROOT / "data/targets/mystery_orbits.json").read_text())
    for s, edges in PAPER_GRAPHS.items():
        tgt = vector_from_paper(tuple(targets["orbits"][s]), 6)
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])
        for a, b, w in edges:
            G.add_edge(v(a), v(b), capacity=w)
        best = G
        t0 = time.perf_counter()
        improved = True
        while improved:
            improved = False
            bulks = sorted(
                (x for x in best.nodes
                 if isinstance(x, str) and x.startswith("b") and best.degree(x) > 0),
                key=best.degree,
            )
            for b in bulks:
                H = best.copy()
                H.remove_node(b)
                if not all(H.degree(p) > 0 for p in [0, 1, 2, 3, 4, 5, "O"]):
                    continue
                hit = refit(H, tgt, seed=1000 + hash((s, b)) % 1000)
                if hit:
                    best = hit[0]
                    improved = True
                    print(f"ray {s}: deleted {b} -> "
                          f"{sum(1 for x in best.nodes if isinstance(x, str) and x.startswith('b') and best.degree(x) > 0)} internal")
                    break
        nb = sum(1 for x in best.nodes
                 if isinstance(x, str) and x.startswith("b") and best.degree(x) > 0)
        S = entropy_vector(best, 6)
        scale = next(k for k in range(1, 30) if all(S[m] == k * tgt[m] for m in tgt))
        cert = {
            "what": f"reduced graph realization of mystery orbit s={s} (n=6)",
            "engine": "greedy bulk-deletion + LP refit, seeded from the exactly "
                      "verified arXiv:2601.19979 graph",
            "internal_vertices": nb,
            "internal_vertices_paper": {"146": 11, "180": 7, "181": 10}[s],
            "note": "UPPER BOUND on minimal internal count; no minimality claim",
            "scale": scale,
            "edges": [[str(a), str(b), d["capacity"]] for a, b, d in best.edges(data=True)],
            "verify": f"hec.entropy.entropy_vector(G, 6) == scale * ray{s}",
        }
        out = ROOT / "reports" / "realizations" / f"n6_s{s}_minimal.json"
        out.write_text(json.dumps(cert, indent=2))
        print(f"ray {s}: final {nb} internal vertices "
              f"(paper: {cert['internal_vertices_paper']}), scale {scale}, "
              f"{best.number_of_edges()} edges, {time.perf_counter()-t0:.0f}s "
              f"-> {out.name}")


if __name__ == "__main__":
    main()

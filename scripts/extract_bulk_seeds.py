#!/usr/bin/env python3
"""Extract published cyclic graph realizations for s=111, s=207 to seed the
Δ-Y search — by matching their Sym(7) orbit against the 4144 HEC6 graph
models in the hecdata repo (SergioHC95/Holographic-Entropy-Cone), then
relabeling the matched graph to OUR representative and verifying it realizes
the ray EXACTLY.

Writes data/targets/bulk_cycle_seeds.json (edges + provenance). If hecdata is
absent or no orbit match is found, writes nothing and reports — the search
loop's seed loader then falls back to random seeds (the ladder still runs).

Usage: extract_bulk_seeds.py [--hecdata /tmp/hecdata]
"""

import argparse
import json
import pathlib
import re
import sys
from functools import reduce
from itertools import permutations
from math import gcd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx

from hec.cone import orbit, permute_vector
from hec.entropy import entropy_vector, entropy_vector_fast
from hec.subsets import vector_from_paper, vector_to_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAB = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "O": "O"}


def primitive(t):
    g = reduce(gcd, (x for x in t if x)) or 1
    return tuple(x // g for x in t)


def parse_graph(line):
    body = line.strip()[1:-1]
    m = re.match(r"\{(.*)\}\s*,\s*\{([^{}]*)\}\s*$", body)
    pairs = re.findall(r'\{\s*"?([A-FOx0-9]+)"?\s*,\s*"?([A-FOx0-9]+)"?\s*\}', m.group(1))
    weights = [int(w) for w in m.group(2).split(",")]
    edges = []
    for (u, v), w in zip(pairs, weights):
        edges.append((LAB.get(u, u), LAB.get(v, v), w))
    return edges


def build(edges):
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])
    for u, v, w in edges:
        G.add_edge(u, v, capacity=w)
    return G


def relabel_graph(edges, perm):
    """perm: tuple over [0..6] (6 == purifier 'O'). Relabel boundary vertices
    by perm; bulk untouched. Returns new edge list."""
    dec = {i: i for i in range(6)}
    dec[6] = "O"
    enc = {**{i: i for i in range(6)}, "O": 6}

    def m(x):
        if isinstance(x, str) and x.startswith("x"):
            return x
        return dec[perm[enc[x]]]

    return [(m(u), m(v), w) for u, v, w in edges]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hecdata", default="/tmp/hecdata")
    args = ap.parse_args()
    gfile = pathlib.Path(args.hecdata) / "n=6" / "graphs.txt"
    if not gfile.exists():
        print(f"hecdata not found at {gfile}; clone "
              "github.com/SergioHC95/Holographic-Entropy-Cone first. "
              "No seeds written (search falls back to random).")
        return

    targets = json.loads((ROOT / "data/targets/bulk_cycle_orbits.json").read_text())
    reps = {s: primitive(tuple(targets["orbits"][s])) for s in ("111", "207")}
    orbits = {s: orbit(vector_from_paper(reps[s], 6), 6) for s in reps}
    perms = list(permutations(range(7)))

    found = {}
    lines = gfile.read_text().strip().splitlines()
    print(f"scanning {len(lines)} hecdata graphs ...")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            edges = parse_graph(line)
            G = build(edges)
            vec = primitive(vector_to_paper(entropy_vector_fast(G, 6), 6))
        except Exception:
            continue
        for s in reps:
            if s in found:
                continue
            if vec in orbits[s]:
                # find perm tau with tau . graph_vec == our representative
                gd = vector_from_paper(vec, 6)
                for perm in perms:
                    if vector_to_paper(permute_vector(gd, perm, 6), 6) == reps[s]:
                        re_edges = relabel_graph(edges, perm)
                        Gr = build(re_edges)
                        S = entropy_vector(Gr, 6)  # exact confirm
                        tgt = vector_from_paper(reps[s], 6)
                        sc = next((k for k in range(1, 40)
                                   if all(S[m] == k * tgt[m] for m in tgt)), None)
                        if sc is not None:
                            used = [v for v in Gr.nodes if Gr.degree(v) > 0]
                            found[s] = {
                                "edges": [[str(u), str(v), w] for u, v, w in re_edges],
                                "scale": sc,
                                "cyclomatic": Gr.number_of_edges() - len(used)
                                + nx.number_connected_components(Gr.subgraph(used)),
                                "hecdata_line": i + 1,
                            }
                            print(f"  s={s}: matched hecdata line {i+1}, "
                                  f"relabeled+verified (scale {sc}, "
                                  f"cyclomatic {found[s]['cyclomatic']})")
                        break
        if len(found) == 2:
            break

    if found:
        out = {
            "what": "published cyclic graph realizations for the bulk-cycle "
                    "orbits, relabeled to our representatives and exactly "
                    "verified; Δ-Y seeds for hec.search",
            "source": "github.com/SergioHC95/Holographic-Entropy-Cone n=6/"
                      "graphs.txt, matched by Sym(7) orbit",
            "seeds": found,
        }
        path = ROOT / "data/targets/bulk_cycle_seeds.json"
        path.write_text(json.dumps(out, indent=2))
        print(f"wrote {path.relative_to(ROOT)} with seeds for {sorted(found)}")
    else:
        print("no orbit match found in hecdata; search falls back to random seeds")


if __name__ == "__main__":
    main()

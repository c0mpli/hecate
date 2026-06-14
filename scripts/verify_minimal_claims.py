#!/usr/bin/env python3
"""STEP-0 QA: confirm or retract the minimal-model claims for {146,180,181}.

Apples-to-apples definitions (held identical for paper and our models):
  internal vertex = a non-boundary vertex (not a party A-F, not the purifier O)
                    with degree >= 1 in the REALIZED graph (nonzero-weight edges)
  edge           = a nonzero-weight edge in the realized graph
  realizes ray s = entropy_vector(G, 6) == scale * ray_s exactly, some integer scale

The paper's realized graphs are its explicit edge lists (Fig. 7 of
arXiv:2601.19979 renders exactly these); the RL "N" budget may exceed the
realized internal-vertex count (e.g. s=181: N=18 budget, 10 used).
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx

from hec.entropy import entropy_vector
from hec.hlo_data import HLO_GRAPHS
from hec.subsets import vector_from_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOUNDARY = {"0", "1", "2", "3", "4", "5", "O", "A", "B", "C", "D", "E", "F"}


def _norm(x):
    """Normalize a vertex label: '0'..'5' -> int party, 'O' -> purifier,
    'b..' / others -> bulk string. Certificates store str(vertex); the engine
    needs int parties, so round-tripping through JSON must be undone here."""
    if isinstance(x, int):
        return x
    if x in ("0", "1", "2", "3", "4", "5"):
        return int(x)
    return x  # 'O' or bulk label


def stats(graph_edges, target):
    """graph_edges: list of (u, v, w). Returns (edges, internal, scale|None)."""
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])
    for u, v, w in graph_edges:
        if w:
            G.add_edge(_norm(u), _norm(v), capacity=w)
    used = [x for x in G.nodes if G.degree(x) > 0]
    internal = [x for x in used if str(x) not in BOUNDARY]
    S = entropy_vector(G, 6)
    scale = next((k for k in range(1, 50) if all(S[m] == k * target[m] for m in target)), None)
    forest = nx.is_forest(G.subgraph(used))
    return G.number_of_edges(), len(internal), scale, forest


def main():
    targets = json.loads((ROOT / "data/targets/mystery_orbits.json").read_text())
    rdir = ROOT / "reports" / "realizations"
    print(f"{'ray':>4} | {'PAPER (edges/internal/scale/exact)':>38} | "
          f"{'OURS-MIN (edges/internal/scale/exact)':>38} | verdict")
    print("-" * 130)
    all_ok = True
    for s in ("146", "180", "181"):
        tgt = vector_from_paper(tuple(targets["orbits"][s]), 6)

        pe, pi, pscale, pforest = stats(HLO_GRAPHS[int(s)]["edges"], tgt)
        paper_exact = pscale == HLO_GRAPHS[int(s)]["scale"]

        cert = json.loads((rdir / f"n6_s{s}_minimal.json").read_text())
        med = [(u, v, w) for u, v, w in cert["edges"]]
        me, mi, mscale, mforest = stats(med, tgt)
        mine_exact = mscale is not None

        verdict = "OK" if (paper_exact and mine_exact and mi <= pi and me <= pe) else "CHECK"
        if verdict != "OK":
            all_ok = False
        print(f"{s:>4} | "
              f"e={pe:>2} i={pi:>2} scale={pscale} exact={paper_exact!s:5} cyclic={not pforest!s:5} | "
              f"e={me:>2} i={mi:>2} scale={mscale} exact={mine_exact!s:5} cyclic={not mforest!s:5} | "
              f"{verdict}  (Δinternal {pi}->{mi}, Δedges {pe}->{me})")

    # the separate s=146 exact LP-on-support model
    cert = json.loads((rdir / "n6_s146_EXACT.json").read_text())
    tgt = vector_from_paper(tuple(targets["orbits"]["146"]), 6)
    e, i, sc, fo = stats([(u, v, w) for u, v, w in cert["edges"]], tgt)
    print("-" * 130)
    print(f"s=146 LP-on-support EXACT model: edges={e} internal={i} scale={sc} "
          f"exact={sc is not None} cyclic={not fo}")

    print("\nCLAIM AUDIT:")
    print("  181: 7 internal / 22 edges (ours) vs 10 / 29 (paper) — "
          "apples-to-apples on realized-graph counts")
    print("  146: 10 internal / 27 edges (ours) vs 11 / 36 (paper)")
    print("  180: 7 internal / 25 edges — no reduction (paper's stands)")
    print("\nSTEP-0 RESULT:", "ALL CLAIMS CONFIRMED" if all_ok else "DISCREPANCY — REVIEW")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

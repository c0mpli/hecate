"""Canonical forms for dedupe (SPEC.md §5 rule 2).

Two objects, two keys:

- vector_key: entropy vectors / rays up to Sym(n+1) — the lex-min orbit
  image (hec.cone.canonical_vector). 720 perms at n=5, 5040 at n=6.

- graph_key: weighted graphs up to isomorphism *fixing each boundary vertex
  individually* (parties are distinguishable; bulk vertices are not).
  pynauty has vertex colors but no edge weights, so each weighted edge is
  subdivided by a middle vertex colored by its weight class; the key is
  (sorted distinct weights, nauty certificate). Equal keys iff the weighted
  graphs are isomorphic over fixed boundary labels.
"""

from __future__ import annotations

import pynauty

from hec.cone import canonical_vector
from hec.entropy import boundary_vertices


def vector_key(S: dict[int, int], n: int) -> tuple:
    return canonical_vector(S, n)


def graph_key(G, n: int, capacity: str = "capacity") -> tuple:
    boundary = boundary_vertices(n)
    bulk = [v for v in G.nodes if v not in boundary]
    order = boundary + bulk  # boundary vertices first, each its own color
    idx = {v: i for i, v in enumerate(order)}

    edges = [(idx[u], idx[v], d[capacity]) for u, v, d in G.edges(data=True) if u != v]
    weights = sorted({w for _, _, w in edges})
    wclass = {w: k for k, w in enumerate(weights)}

    nv = len(order) + len(edges)  # original vertices + one middle per edge
    adj: dict[int, list[int]] = {i: [] for i in range(nv)}
    wgroups: dict[int, set[int]] = {k: set() for k in range(len(weights))}
    for e, (u, v, w) in enumerate(edges):
        mid = len(order) + e
        adj[u].append(mid)
        adj[v].append(mid)
        wgroups[wclass[w]].add(mid)

    coloring = [{idx[v]} for v in boundary]            # each boundary vertex fixed
    coloring.append(set(range(len(boundary), len(order))))  # bulk interchangeable
    coloring += [wgroups[k] for k in range(len(weights))]   # weight classes
    coloring = [c for c in coloring if c]

    g = pynauty.Graph(nv, directed=False, adjacency_dict=adj, vertex_coloring=coloring)
    return (tuple(weights), pynauty.certificate(g))

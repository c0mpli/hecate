"""Boundary-vertex splitting: cyclic models -> non-simple trees.

The transform behind fig. N5trees of arXiv:2204.00075: replace every
boundary vertex of degree k by k degree-1 copies carrying the same party
label (one incident edge each). Bulk-boundary cycles break; pure-bulk
cycles survive. Whether the entropy vector is preserved is NOT automatic —
each split graph must be re-verified with the labeled engine.

Derived fact (session 5): splitting our verified published C5 models
preserves the entropy vector exactly for all ten non-chordal rays, and
yields trees for eight of them (11-16, 18, 19). Rays 10 and 17 retain
pure-bulk cycles (the class 2204.00075 handles with Delta-Y-type operations)
— they are the hard rung-1 validation targets for the party-splitting
annealer.
"""

from __future__ import annotations

import networkx as nx


def split_boundary(edges, bulk_prefix: str = "b"):
    """Edge list -> (split graph, party map). Bulk vertices (prefix names)
    are untouched; each boundary vertex x becomes copies 'x#0', 'x#1', ...
    labeled by party x."""
    H = nx.Graph()
    party: dict = {}
    counters: dict = {}
    def is_bulk(x):
        return isinstance(x, str) and x.startswith(bulk_prefix)
    def copy_of(x):
        k = counters.get(x, 0)
        counters[x] = k + 1
        name = f"{x}#{k}"
        party[name] = x
        return name
    for u, v, w in edges:
        uu = u if is_bulk(u) else copy_of(u)
        vv = v if is_bulk(v) else copy_of(v)
        H.add_edge(uu, vv, capacity=w)
    return H, party

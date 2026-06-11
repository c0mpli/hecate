"""Entropy vectors of weighted graphs via min-cut.

The graph model (BNOSSW, arXiv:1505.07839 §2): an entropy vector is
holographic iff it is realized by an undirected graph with non-negative edge
weights, where the boundary vertices are the n parties plus a purifier O and

    S(I) = total weight of a minimum cut separating the boundary vertices
           in I from the rest of the boundary,

with bulk vertices free to fall on either side of the cut.

Conventions used throughout the toolkit:
- Parties are the integer vertices 0..n-1; the purifier is the vertex "O".
  Bulk vertices are any other hashable labels (we use "b0", "b1", ...).
- A subset of parties is a bitmask: bit i set <=> party i in the subset.
- An entropy vector is a dict {mask: S} for mask = 1 .. 2**n - 1.
- Edge weights live in the "capacity" attribute. Integer (or Fraction)
  weights make every S(I) exact, since min-cut only adds and compares
  weights. All search generators emit integer weights; floats are allowed
  for exploration but are never evidence (SPEC.md §5 rule 1).
"""

from __future__ import annotations

import networkx as nx

PURIFIER = "O"
_SRC = "_src"
_SNK = "_snk"


def subset_label(mask: int, n: int) -> str:
    """Human-readable name for a party bitmask, e.g. 0b101 -> "AC"."""
    return "".join(chr(ord("A") + i) for i in range(n) if mask >> i & 1)


def boundary_vertices(n: int) -> list:
    return list(range(n)) + [PURIFIER]


def entropy_vector(G: nx.Graph, n: int, capacity: str = "capacity") -> dict[int, object]:
    """Compute S(I) for every nonempty subset I of the n parties.

    Each S(I) is one s-t min-cut: a super-source is wired to the parties in I
    and a super-sink to the remaining boundary (including the purifier) with
    uncapacitated edges, which networkx treats as infinite capacity.

    Raises if a boundary vertex is missing from G. Parallel edges (MultiGraph)
    and self-loops are handled by merging and dropping respectively.
    """
    boundary = boundary_vertices(n)
    missing = [v for v in boundary if v not in G]
    if missing:
        raise ValueError(f"graph is missing boundary vertices {missing}")

    # Simple working copy with merged parallel edges and no self-loops.
    H = nx.Graph()
    H.add_nodes_from(G.nodes)
    for u, v, data in G.edges(data=True):
        if u == v:
            continue
        w = data[capacity]
        if w < 0:
            raise ValueError(f"negative weight on edge ({u}, {v})")
        if H.has_edge(u, v):
            H[u][v][capacity] += w
        else:
            H.add_edge(u, v, **{capacity: w})
    H.add_node(_SRC)
    H.add_node(_SNK)

    S: dict[int, object] = {}
    for mask in range(1, 1 << n):
        inside = [i for i in range(n) if mask >> i & 1]
        outside = [v for v in boundary if not (isinstance(v, int) and mask >> v & 1)]
        H.add_edges_from((_SRC, v) for v in inside)   # no capacity attr = infinite
        H.add_edges_from((_SNK, v) for v in outside)
        value, _ = nx.minimum_cut(H, _SRC, _SNK, capacity=capacity)
        S[mask] = value
        H.remove_edges_from(list(H.edges(_SRC)))
        H.remove_edges_from(list(H.edges(_SNK)))
    return S


def format_vector(S: dict[int, object], n: int) -> str:
    """One-line rendering in subset order A, B, AB, C, AC, BC, ABC, ..."""
    return ", ".join(f"S({subset_label(m, n)})={S[m]}" for m in sorted(S))

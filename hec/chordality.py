"""The chordality criterion for simple-tree/forest realizability.

Theorem (Hubeny-Rota, arXiv:2512.24490, building on 2412.18018 and
2512.18702): an entropy vector satisfying SA and SSA is realizable by a
holographic SIMPLE FOREST graph model (one boundary vertex per party, no
cycles) if and only if the line graph of its correlation hypergraph is
chordal. For irreducible vectors, "forest" upgrades to "tree". The proof is
constructive: chordal vectors come with an explicit tree-building algorithm.

Operational pipeline implemented here (all exact integer arithmetic):
  1. MI instances over the n+1 labels (purifier = label n), evaluated via
     purification: I(X:Y) = S(X) + S(Y) - S(XY), with S(full) = 0.
  2. PMI = the set of vanishing instances.
  3. B-set of X (|X| >= 2) = all bipartitions {Y, Z} of X; B(X) is positive
     iff no bipartition has vanishing mutual information.
  4. Correlation hypergraph: vertices = labels, hyperedges = {X : B(X) > 0}.
  5. Criterion: nx.is_chordal(line graph of the hypergraph).

What a FAIL means for a suspect ray: no simple-forest model exists, period
(theorem, not heuristic). It says nothing by itself about non-simple trees
or graphs with cycles; combined with the strong tree conjecture
(arXiv:2204.00075) it would imply non-realizability, but that implication
is conditional on the conjecture.
"""

from __future__ import annotations

from itertools import combinations

import networkx as nx

from hec.cone import _reduce


def _subset_entropy(S: dict[int, int], Z: int, n: int) -> int:
    """Entropy of a subsystem given as a mask over the n+1 labels."""
    full = (1 << (n + 1)) - 1
    if Z == full or Z == 0:
        return 0
    return S[_reduce(Z, n)]


def mutual_information(S: dict[int, int], X: int, Y: int, n: int) -> int:
    return (
        _subset_entropy(S, X, n)
        + _subset_entropy(S, Y, n)
        - _subset_entropy(S, X | Y, n)
    )


def bset_positive(S: dict[int, int], X: int, n: int) -> bool:
    """True iff every bipartition {Y, Z} of X has I(Y:Z) > 0."""
    members = [i for i in range(n + 1) if X >> i & 1]
    anchor = members[0]
    rest = members[1:]
    for r in range(0, len(rest) + 1):
        for sub in combinations(rest, r):
            Y = (1 << anchor) | sum(1 << i for i in sub)
            Z = X & ~Y
            if Z == 0:
                continue
            if mutual_information(S, Y, Z, n) == 0:
                return False
    return True


def correlation_hypergraph(S: dict[int, int], n: int) -> list[int]:
    """Hyperedges (masks over n+1 labels) whose B-set is positive."""
    full = (1 << (n + 1)) - 1
    out = []
    for X in range(3, full + 1):
        if bin(X).count("1") >= 2 and bset_positive(S, X, n):
            out.append(X)
    return out


def line_graph(hyperedges: list[int]) -> nx.Graph:
    L = nx.Graph()
    L.add_nodes_from(range(len(hyperedges)))
    for i, j in combinations(range(len(hyperedges)), 2):
        if hyperedges[i] & hyperedges[j]:
            L.add_edge(i, j)
    return L


def simple_forest_realizable(S: dict[int, int], n: int) -> dict:
    """Apply the chordality criterion. S must satisfy SA and SSA (caller's
    responsibility; the suspects were verified in verify_er6)."""
    H = correlation_hypergraph(S, n)
    L = line_graph(H)
    chordal = nx.is_chordal(L)
    return {
        "chordal": chordal,
        "hyperedges": len(H),
        "line_graph_nodes": L.number_of_nodes(),
        "line_graph_edges": L.number_of_edges(),
        "verdict": (
            "simple-forest realizable (constructively)" if chordal
            else "NOT realizable by any simple forest (theorem)"
        ),
    }

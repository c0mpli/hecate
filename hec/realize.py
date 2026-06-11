"""Graph realization search: target entropy vector -> weighted graph.

v1 (M3 scaffold): stochastic hill-climb over (tree-biased topology, integer
edge weights), exact objective, exact verification of hits. Any returned
graph G satisfies entropy_vector(G) == scale * target exactly — float never
touches a claim. The principled (topology, cut-assignment) -> LP-feasibility
engine of SPEC.md §6 replaces the inner loop later; negative results from
this module are NOT exclusion evidence, only absence of luck.
"""

from __future__ import annotations

import random

from hec.entropy import entropy_vector, entropy_vector_fast, prepare_fast
from hec.graphs import random_connected, random_tree
from hec.subsets import vector_from_paper


def _score(G, n, tgt):
    S = entropy_vector_fast(G, n)
    return sum(abs(S[m] - tgt[m]) for m in tgt)


def _star(n, rng, wmax):
    """One bulk hub joined to every boundary vertex (rays 1-7 of C5 live here)."""
    import networkx as nx

    from hec.entropy import boundary_vertices

    G = nx.Graph()
    for v in boundary_vertices(n):
        G.add_edge("b0", v, capacity=rng.randint(1, wmax))
    return G


def _double_star(n, rng, wmax):
    """Two bridged bulk hubs with the boundary split between them."""
    import networkx as nx

    from hec.entropy import boundary_vertices

    G = nx.Graph()
    G.add_edge("b0", "b1", capacity=rng.randint(1, wmax))
    for v in boundary_vertices(n):
        G.add_edge(rng.choice(("b0", "b1")), v, capacity=rng.randint(1, wmax))
    return G


def realize_target(
    target,
    n: int,
    rng: random.Random,
    scales=(1, 2),
    bulk_range=(0, 6),
    restarts: int = 60,
    moves: int = 1500,
    allow_cycles: bool = False,
):
    """Search for a graph realizing `target` (paper-order tuple or mask dict).

    Returns (G, scale) with entropy_vector(G, n) == scale * target verified
    in the exact reference path, or None.
    """
    tgt0 = target if isinstance(target, dict) else vector_from_paper(target, n)

    for r in range(restarts):
        k = scales[r % len(scales)]
        tgt = {m: k * v for m, v in tgt0.items()}
        wmax = max(tgt.values()) or 1
        b = rng.randint(*bulk_range)
        roll = rng.random()
        if roll < 0.2:
            G = _star(n, rng, wmax)
        elif roll < 0.35:
            G = _double_star(n, rng, wmax)
        elif allow_cycles and roll < 0.6:
            G = random_connected(n, rng, n_bulk=b, extra_edges=rng.randint(1, 3), wmax=wmax)
        else:
            G = random_tree(n, rng, n_bulk=b, wmax=wmax)
        best = _score(G, n, tgt)
        stall = 0
        for _ in range(moves):
            if best == 0:
                break
            u, v = rng.choice(list(G.edges))
            old = G[u][v]["capacity"]
            roll = rng.random()
            if roll < 0.45:
                new = old + rng.choice((-1, 1))
            elif roll < 0.9:
                new = old + rng.choice((-3, -2, 2, 3))
            else:
                new = rng.randint(0, wmax)
            if new < 0:
                continue
            G[u][v]["capacity"] = new
            s = _score(G, n, tgt)
            if s <= best:  # sideways moves allowed
                stall = stall + 1 if s == best else 0
                best = s
            else:
                G[u][v]["capacity"] = old
                stall += 1
            if stall > 250:
                break
        if best == 0:
            S = entropy_vector(G, n)  # exact reference path, the actual claim
            assert S == tgt, "fast path disagreed with exact path"
            G.remove_edges_from(
                [(u, v) for u, v, d in G.edges(data=True) if d["capacity"] == 0]
            )
            return G, k
    return None

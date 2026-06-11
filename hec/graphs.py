"""Random graph generators for engine verification and (later) the hunts.

Day-1 scope: simple mixtures with integer weights — stars, random trees with
bulk vertices, and trees with extra edges (bulk cycles). Tree-biased priors,
mutation operators and nauty canonicalization arrive with M1-M2.

All generators emit integer weights so every downstream entropy and
inequality check is exact.
"""

from __future__ import annotations

import random

import networkx as nx

from hec.entropy import PURIFIER, boundary_vertices


def random_star(n: int, rng: random.Random, wmax: int = 64) -> nx.Graph:
    """One bulk center joined to every boundary vertex."""
    G = nx.Graph()
    for v in boundary_vertices(n):
        G.add_edge("b0", v, capacity=rng.randint(1, wmax))
    return G


def random_tree(n: int, rng: random.Random, n_bulk: int = 2, wmax: int = 64) -> nx.Graph:
    """Random tree on the boundary plus n_bulk bulk vertices.

    Built by sequential random attachment over a shuffled vertex order:
    every labeled tree is reachable, boundary vertices may be internal.
    """
    vertices = boundary_vertices(n) + [f"b{i}" for i in range(n_bulk)]
    rng.shuffle(vertices)
    G = nx.Graph()
    G.add_node(vertices[0])
    for i, v in enumerate(vertices[1:], start=1):
        u = vertices[rng.randrange(i)]
        G.add_edge(u, v, capacity=rng.randint(1, wmax))
    return G


def random_connected(
    n: int,
    rng: random.Random,
    n_bulk: int = 2,
    extra_edges: int = 2,
    wmax: int = 64,
) -> nx.Graph:
    """Random tree plus extra random edges — introduces bulk cycles."""
    G = random_tree(n, rng, n_bulk=n_bulk, wmax=wmax)
    vertices = list(G.nodes)
    for _ in range(extra_edges):
        u, v = rng.sample(vertices, 2)
        if not G.has_edge(u, v):
            G.add_edge(u, v, capacity=rng.randint(1, wmax))
    return G


def random_mixture(n: int, rng: random.Random, wmax: int = 64) -> nx.Graph:
    """The Day-1 verification mixture: stars, trees, and cyclic graphs."""
    roll = rng.random()
    if roll < 0.25:
        return random_star(n, rng, wmax=wmax)
    if roll < 0.65:
        return random_tree(n, rng, n_bulk=rng.randint(0, 4), wmax=wmax)
    return random_connected(
        n, rng, n_bulk=rng.randint(0, 4), extra_edges=rng.randint(1, 4), wmax=wmax
    )

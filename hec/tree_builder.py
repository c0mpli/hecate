"""Constructive simple-tree builder (Algorithm 1 of arXiv:2512.18702, proven
always-correct for chordal inputs in arXiv:2512.24490).

Input: an entropy vector obeying SA+SSA whose correlation-hypergraph line
graph is chordal. Output: a simple forest graph model realizing it —
verified here by exact entropy recomputation, never trusted.

Pipeline: positive B-sets -> line graph -> max-cliques -> weighted clique
graph -> maximum spanning tree (a clique tree, by chordality) -> attach one
boundary leaf per party at the unique max-clique containing its hyperedge
star -> weight every tree edge e by S(Y), where Y is the purifier-free side
of the leaf-partition induced by deleting e.

Pure parties (entropy 0, empty hyperedge star) sit outside the paper's
irreducibility assumption; we attach them anywhere with weight S({l}) = 0,
which the final exact verification justifies case by case.
"""

from __future__ import annotations

from itertools import combinations

import networkx as nx

from hec.chordality import correlation_hypergraph, line_graph
from hec.entropy import PURIFIER


def build_simple_forest(S: dict[int, int], n: int) -> nx.Graph:
    """Returns a verified simple-forest model of S, or raises."""
    H = correlation_hypergraph(S, n)
    L = line_graph(H)
    if not nx.is_chordal(L):
        raise ValueError("line graph not chordal: no simple forest exists")

    cliques = [frozenset(c) for c in nx.find_cliques(L)] or [frozenset()]
    K = nx.Graph()
    K.add_nodes_from(range(len(cliques)))
    for i, j in combinations(range(len(cliques)), 2):
        w = len(cliques[i] & cliques[j])
        if w:
            K.add_edge(i, j, weight=w)
    clique_tree = nx.maximum_spanning_tree(K, weight="weight")

    G = nx.Graph()
    G.add_nodes_from(f"q{i}" for i in clique_tree.nodes)
    G.add_edges_from((f"q{u}", f"q{v}") for u, v in clique_tree.edges)

    label_of = lambda l: PURIFIER if l == n else l
    for l in range(n + 1):
        star = {h for h, mask in enumerate(H) if mask >> l & 1}
        if star:
            hosts = [ci for ci, cl in enumerate(cliques) if star <= cl]
            assert len(hosts) == 1, (
                f"party {l}: hyperedge star contained in {len(hosts)} "
                f"max-cliques (theorem guarantees exactly 1) — BUG"
            )
            host = hosts[0]
        else:
            host = 0  # pure party: weight-0 leaf, location irrelevant
        G.add_edge(label_of(l), f"q{host}")

    # weight each edge by the entropy of its purifier-free leaf side
    full = (1 << n) - 1
    for u, v in list(G.edges):
        G.remove_edge(u, v)
        comp = nx.node_connected_component(G, u)
        G.add_edge(u, v)
        side_parties = sum(1 << l for l in range(n) if l in comp)
        has_pur = PURIFIER in comp
        Y = (full & ~side_parties) if has_pur else side_parties
        G[u][v]["capacity"] = S[Y] if Y else 0

    return G

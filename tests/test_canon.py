"""Canonicalization: equivalent objects collide, inequivalent ones don't."""

import random

import networkx as nx
import pytest

pytest.importorskip("pynauty")  # graph keys need nauty; skip cleanly without

from hec.canon import graph_key, vector_key
from hec.entropy import PURIFIER, entropy_vector
from hec.graphs import random_tree
from hec.subsets import vector_from_paper


def relabeled_bulk(G, mapping):
    return nx.relabel_nodes(G, mapping)


def test_graph_key_invariant_under_bulk_relabeling():
    rng = random.Random(3)
    for _ in range(20):
        G = random_tree(3, rng, n_bulk=3)
        H = relabeled_bulk(G, {"b0": "x", "b1": "y", "b2": "z"})
        assert graph_key(G, 3) == graph_key(H, 3)


def test_graph_key_detects_weight_change():
    G = nx.Graph()
    for v, w in [(0, 1), (1, 2), (2, 3), (PURIFIER, 4)]:
        G.add_edge("b0", v, capacity=w)
    H = G.copy()
    H["b0"][0]["capacity"] = 5
    assert graph_key(G, 3) != graph_key(H, 3)


def test_graph_key_fixes_boundary_identity():
    # swapping two parties' attachments is NOT the same labelled graph
    G = nx.Graph()
    for v, w in [(0, 1), (1, 2), (2, 3), (PURIFIER, 4)]:
        G.add_edge("b0", v, capacity=w)
    H = nx.Graph()
    for v, w in [(0, 2), (1, 1), (2, 3), (PURIFIER, 4)]:  # A and B swapped
        H.add_edge("b0", v, capacity=w)
    assert graph_key(G, 3) != graph_key(H, 3)
    # ... but their entropy vectors are in the same Sym(n+1) orbit
    assert vector_key(entropy_vector(G, 3), 3) == vector_key(entropy_vector(H, 3), 3)


def test_vector_key_collapses_purifier_swap():
    # Bell pair A-O vs Bell pair A-B: same orbit under Sym(4) at n=3
    bell_ao = vector_from_paper((1, 0, 0, 1, 1, 0, 1), 3)   # order A,B,C,AB,AC,BC,ABC
    bell_ab = vector_from_paper((1, 1, 0, 0, 1, 1, 0), 3)
    assert vector_key(bell_ao, 3) == vector_key(bell_ab, 3)

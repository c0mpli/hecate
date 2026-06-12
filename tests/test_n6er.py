"""N6er1/N6er3 transcriptions: SA+SSA hold, SAC-extremality ranks locked."""

import networkx as nx
import sympy

from hec.cone import sa_instances
from hec.entropy import entropy_vector
from hec.n6er_data import N6ER1_EDGES, N6ER3_EDGES
from hec.subsets import vector_to_paper


def _rank(edges):
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])
    for u, v, w in edges:
        G.add_edge(u, v, capacity=w)
    vec = vector_to_paper(entropy_vector(G, 6), 6)
    SA = sa_instances(6)
    assert all(sum(a * b for a, b in zip(f, vec)) >= 0 for f in SA)
    sat = [f for f in SA if sum(a * b for a, b in zip(f, vec)) == 0]
    return sympy.Matrix(sat).rank()


def test_n6er_models_not_sac_extreme():
    assert _rank(N6ER1_EDGES) == 58
    assert _rank(N6ER3_EDGES) == 61

"""All 19 published C5 graph models reproduce their claimed rays exactly."""

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.entropy import entropy_vector
from hec.subsets import vector_from_paper


def test_all_19_published_graphs_verified():
    for k in range(1, 20):
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3, 4, "O"])
        for u, v, w in C5_PUBLISHED_GRAPHS[k]:
            G.add_edge(u, v, capacity=w)
        S = entropy_vector(G, 5)
        tgt = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
        assert any(
            all(S[m] == s * tgt[m] for m in tgt) for s in (1, 2)
        ), f"graph {k} does not reproduce ray {k}"

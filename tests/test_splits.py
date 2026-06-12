"""Split-trees: derived rung-1 oracle set, exactly verified."""

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.entropy import entropy_vector, entropy_vector_labeled
from hec.splits import split_boundary
from hec.subsets import vector_from_paper

TREE_AFTER_SPLIT = {11, 12, 13, 14, 15, 16, 18, 19}
BULK_CYCLE_SURVIVES = {10, 17}


def test_split_preserves_entropy_and_tree_status():
    for k in range(10, 20):
        edges = C5_PUBLISHED_GRAPHS[k]
        G0 = nx.Graph()
        G0.add_nodes_from([0, 1, 2, 3, 4, "O"])
        for u, v, w in edges:
            G0.add_edge(u, v, capacity=w)
        S0 = entropy_vector(G0, 5)

        H, party = split_boundary(edges)
        S = entropy_vector_labeled(H, 5, party)
        assert S == S0, f"ray {k}: splitting changed the vector"
        assert nx.is_forest(H) == (k in TREE_AFTER_SPLIT), f"ray {k}"

        tgt = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
        scale = next(s for s in (1, 2) if all(S0[m] == s * tgt[m] for m in tgt))
        assert all(S[m] == scale * tgt[m] for m in tgt)

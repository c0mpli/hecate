"""HLO realizations of {146, 180, 181}: exact verification + tripwire."""

import json
import pathlib

import networkx as nx

from hec.entropy import entropy_vector
from hec.hlo_data import HLO_GRAPHS
from hec.subsets import vector_from_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_hlo_graphs_exact_and_cyclic():
    targets = json.loads((ROOT / "data/targets/mystery_orbits.json").read_text())
    for s, spec in HLO_GRAPHS.items():
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])
        for u, v, w in spec["edges"]:
            G.add_edge(u, v, capacity=w)
        tgt = vector_from_paper(tuple(targets["orbits"][str(s)]), 6)
        S = entropy_vector(G, 6)
        assert all(S[m] == spec["scale"] * tgt[m] for m in tgt), f"s={s} not exact"
        used = [x for x in G.nodes if G.degree(x) > 0]
        # simple by construction; a forest here would contradict chordality
        assert not nx.is_forest(G.subgraph(used)), f"s={s} forest — tripwire!"

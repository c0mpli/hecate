"""HLO realizations of {146, 180, 181}: exact verification + tripwire."""

import json
import pathlib

import networkx as nx

from hec.entropy import entropy_vector
from hec.hlo_data import HLO_GRAPHS
from hec.subsets import vector_from_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _norm(x):
    if x in ("0", "1", "2", "3", "4", "5"):
        return int(x)
    return x


def test_minimal_models_exact_and_not_larger():
    """Email-grade claim guard: each minimal cert realizes its ray exactly and
    is no larger than the paper's published model (same internal-vertex defn)."""
    targets = json.loads((ROOT / "data/targets/mystery_orbits.json").read_text())
    paper = {"146": (36, 11), "180": (25, 7), "181": (29, 10)}
    ours = {"146": (27, 10), "180": (25, 7), "181": (22, 7)}
    boundary = {"0", "1", "2", "3", "4", "5", "O"}
    for s in ("146", "180", "181"):
        cert = json.loads((ROOT / f"reports/realizations/n6_s{s}_minimal.json").read_text())
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])
        for u, v, w in cert["edges"]:
            if w:
                G.add_edge(_norm(u), _norm(v), capacity=w)
        tgt = vector_from_paper(tuple(targets["orbits"][s]), 6)
        S = entropy_vector(G, 6)
        scale = next(k for k in range(1, 50) if all(S[m] == k * tgt[m] for m in tgt))
        assert scale is not None
        used = [x for x in G.nodes if G.degree(x) > 0]
        internal = sum(1 for x in used if str(x) not in boundary)
        assert (G.number_of_edges(), internal) == ours[s], f"s={s} counts drifted"
        assert internal <= paper[s][1] and G.number_of_edges() <= paper[s][0]


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

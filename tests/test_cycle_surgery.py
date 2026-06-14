"""Cycle surgery: exact moves + the binding C5 10/17 validation gate."""

from fractions import Fraction

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.cycle_surgery import (
    cyclomatic,
    moves_delta_y,
    moves_y_delta,
    normalize,
    surgery,
)
from hec.entropy import entropy_vector_labeled
from hec.subsets import vector_from_paper


def _seed(k, n=5):
    G = nx.Graph()
    party = {}
    for lab in list(range(n)) + ["O"]:
        G.add_node(lab)
        party[lab] = lab
    for u, v, w in C5_PUBLISHED_GRAPHS[k]:
        G.add_edge(u, v, capacity=Fraction(w))
    return G, party


def test_delta_y_preserves_entropy_and_reduces_cycle():
    # a graph with a bulk triangle
    G = nx.Graph()
    party = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, "O": "O"}
    for lab in party:
        G.add_node(lab)
    for u, v, w in [(0, "a", 2), (1, "b", 2), (2, "c", 2), (3, "a", 1), (4, "b", 1),
                    ("O", "c", 1), ("a", "b", 1), ("b", "c", 1), ("a", "c", 1)]:
        G.add_edge(u, v, capacity=Fraction(w))
    before = entropy_vector_labeled(G, 5, party)
    got = list(moves_delta_y(G, party))
    assert got, "no triangle found"
    H, p, _ = got[0]
    assert entropy_vector_labeled(H, 5, p) == before  # Δ→Y exact
    assert cyclomatic(H) == cyclomatic(G) - 1


def test_y_delta_inverts_delta_y():
    G = nx.Graph()
    party = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, "O": "O"}
    for lab in party:
        G.add_node(lab)
    for u, v, w in [(0, "a", 2), (1, "b", 2), (2, "c", 2), (3, "a", 1), (4, "b", 1),
                    ("O", "c", 1), ("a", "b", 1), ("b", "c", 1), ("a", "c", 1)]:
        G.add_edge(u, v, capacity=Fraction(w))
    before = entropy_vector_labeled(G, 5, party)
    H, p, _ = next(moves_delta_y(G, party))
    back = next(moves_y_delta(H, p))
    assert entropy_vector_labeled(back[0], 5, back[1]) == before


def _gate(k):
    G, party = _seed(k)
    tgt = entropy_vector_labeled(G, 5, party)
    path, info = surgery(G, party, 5, f"c5_{k}", target=tgt, max_nodes=6000,
                         max_depth=30, out_dir=__import__("pathlib").Path("/tmp/surg_test"),
                         log=lambda m: None)
    assert info["status"] == "tree", f"ray {k}: surgery failed to find a tree"
    import json
    cert = json.loads(path.read_text())
    H = nx.Graph()
    p = {}
    nrm = lambda x: int(x) if x in ("0", "1", "2", "3", "4", "5") else x
    for u, v, w in cert["edges"]:
        H.add_edge(nrm(u), nrm(v), capacity=w)
    for vk, lab in cert["party"].items():
        p[nrm(vk)] = nrm(lab) if isinstance(lab, str) and lab.isdigit() else lab
    assert nx.is_forest(H)
    S = entropy_vector_labeled(H, 5, p)
    ray = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
    assert any(all(S[m] == s * ray[m] for m in ray) for s in range(1, 40))


def test_gate_ray10():
    _gate(10)


def test_gate_ray17():
    _gate(17)

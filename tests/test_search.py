"""hec/search.py: the keep/discard loop finds + exactly certifies a tree for
a known-realizable C5 ladder ray (the gate's fast CI proxy)."""

import random

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.entropy import entropy_vector_labeled
from hec.search import POLICY, cyclomatic, search
from hec.subsets import vector_from_paper


def _norm(x):
    return int(x) if isinstance(x, str) and x in ("0", "1", "2", "3", "4", "5") else x


def test_search_finds_tree_for_c5_ray11(tmp_path):
    pol = dict(POLICY)
    pol["budget_iters"] = 600
    pol["budget_seconds"] = 120
    pol["log_every"] = 10 ** 9
    path = search(C5_EXTREME_RAYS[10], 5, "c5_11", random.Random(1),
                  policy=pol, log=lambda m: None, out_dir=tmp_path)
    assert path is not None, "loop failed to find a known-existing tree for ray 11"

    import json
    cert = json.loads(path.read_text())
    assert cert["verified"] is True and cert["is_forest"] is True
    G = nx.Graph()
    party = {}
    for u, v, w in cert["edges"]:
        G.add_edge(_norm(u), _norm(v), capacity=w)
    for vk, lab in cert["party"].items():
        party[_norm(vk)] = _norm(lab) if isinstance(lab, str) and lab.isdigit() else lab
    assert nx.is_forest(G)
    S = entropy_vector_labeled(G, 5, party)
    tgt = vector_from_paper(C5_EXTREME_RAYS[10], 5)
    assert all(S[m] == cert["scale"] * tgt[m] for m in tgt)


def test_cyclomatic():
    G = nx.cycle_graph(4)
    assert cyclomatic(G) == 1
    T = nx.path_graph(4)
    assert cyclomatic(T) == 0

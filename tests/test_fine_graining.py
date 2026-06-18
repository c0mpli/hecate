"""fine_graining: the coarse-graining round-trip (the flagged correctness risk),
the purifier-split regression, and the C5 10/17 validation gate."""

from fractions import Fraction

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.chordality import simple_forest_realizable
from hec.entropy import entropy_vector_labeled
from hec.fine_graining import (
    coarse_grain,
    fine_graining_realizable,
    refined_vector,
    relabel_to_simple,
)
from hec.subsets import vector_from_paper


def _nonsimple_star(n=3):
    """A non-simple tree: party 0 labels two leaves; one bulk hub."""
    G = nx.Graph()
    party = {}
    edges = [("a1", "x", 2), ("a2", "x", 3), ("b", "x", 1), ("c", "x", 1),
             ("o", "x", 2)]
    for u, v, w in edges:
        G.add_edge(u, v, capacity=Fraction(w))
    party = {"a1": 0, "a2": 0, "b": 1, "c": 2, "o": "O"}
    return G, party


def test_coarse_grain_round_trip():
    # the lifting/coarse-graining must reproduce the labeled-entropy ground truth
    G, party = _nonsimple_star()
    labeled = entropy_vector_labeled(G, 3, party)
    Gs, n_prime, cg, rpmap = relabel_to_simple(G, party)
    Sprime = refined_vector(Gs, n_prime, rpmap)
    back = coarse_grain(Sprime, cg, n_prime, 3)
    assert back == labeled


def test_refined_tree_is_simple_and_chordal():
    # regression for the purifier-split bug: the refined tree must be SIMPLE
    # (one boundary vertex per refined label, single purifier) hence CHORDAL
    G, party = _nonsimple_star()
    Gs, n_prime, cg, rpmap = relabel_to_simple(G, party)
    counts = {}
    for v, lab in rpmap.items():
        counts[lab] = counts.get(lab, 0) + 1
    assert all(c == 1 for c in counts.values()), "refined tree not simple"
    assert simple_forest_realizable(refined_vector(Gs, n_prime, rpmap), n_prime)["chordal"]


def _c5_seed(k):
    G = nx.Graph()
    party = {}
    for lab in [0, 1, 2, 3, 4, "O"]:
        G.add_node(lab)
        party[lab] = lab
    for u, v, w in C5_PUBLISHED_GRAPHS[k]:
        G.add_edge(u, v, capacity=Fraction(w))
    return G, party


def _gate(k, tmp_path):
    G, party = _c5_seed(k)
    S = entropy_vector_labeled(G, 5, party)
    cert, info = fine_graining_realizable(f"c5_{k}", S, 5, bound=4,
                                          cyclic_seed=(G, party), out_dir=tmp_path,
                                          log=lambda m: None)
    assert info["status"] == "tree"
    assert cert is not None and cert["refined_chordal"] is True
    # independent re-check: refined chordal + coarse-grains exactly
    assert cert["verified"] is True


def test_gate_ray10(tmp_path):
    _gate(10, tmp_path)


def test_gate_ray17(tmp_path):
    _gate(17, tmp_path)

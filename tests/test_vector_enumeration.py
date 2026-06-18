"""vector_enumeration soundness tests — regressions for the two bugs the gates
caught, plus the generation-equivalence check (optimization soundness).

The expensive GATE 1/GATE 2 (decide must find known trees for real C5 rays)
run as scripts (scripts/ve_gates.py) — too slow for CI — and their results are
reported in NOTES. These tests cover the soundness-critical primitives."""

import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.splits import split_boundary
from hec.vector_enumeration import (
    _canon_colored_tree,
    colored_trees,
    split_structures,
)


def test_canon_key_is_isomorphism_invariant():
    """Regression: color classes must be canonically ordered, else isomorphic
    colored trees get different keys and the dedup is unsound (drops/collides
    structures). GATE 1 caught this."""
    H, party = split_boundary(C5_PUBLISHED_GRAPHS[11])
    keyH = _canon_colored_tree(H, party)
    # random relabeling must not change the key
    mapping = {v: ("z", i) for i, v in enumerate(H.nodes)}
    H2 = nx.relabel_nodes(H, mapping)
    p2 = {mapping[v]: party[v] for v in party}
    assert _canon_colored_tree(H2, p2) == keyH

    # an isomorphic colored tree built independently must share the key
    Hc = nx.Graph(H)
    for v in Hc:
        Hc.nodes[v]["lab"] = str(party.get(v, "_bulk"))
    nm = categorical_node_match("lab", "")
    mult = {}
    for lab in party.values():
        mult[lab] = mult.get(lab, 0) + 1
    nb = sum(1 for v in H if v not in party)
    found = False
    for T, p in colored_trees(5, mult, nb):
        Tc = nx.Graph(T)
        for v in Tc:
            Tc.nodes[v]["lab"] = str(p.get(v, "_bulk"))
        if nx.is_isomorphic(Hc, Tc, node_match=nm):
            assert _canon_colored_tree(T, p) == keyH  # iso => same key
            found = True
            break
    assert found, "the known ray-11 tree structure must be enumerated"


def test_generation_equivalence_multiset_vs_allperms():
    """The multiset-permutation optimization must yield the IDENTICAL distinct
    set as naive all-permutations (the soundness gate for the speedup)."""
    for n_extra in (1, 2):
        for mult in split_structures(5, n_extra)[:3]:
            for nb in (1, 2):
                old = {_canon_colored_tree(T, p)
                       for T, p in colored_trees(5, mult, nb, _use_multiset=False)}
                new = {_canon_colored_tree(T, p)
                       for T, p in colored_trees(5, mult, nb, _use_multiset=True)}
                assert old == new, f"n_extra={n_extra} mult={mult} nb={nb}"

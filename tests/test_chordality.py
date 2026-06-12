"""Chordality criterion: locked to the 19-ray ground truth + the gate result."""

import json
import pathlib

from hec.c5_data import C5_EXTREME_RAYS
from hec.chordality import simple_forest_realizable
from hec.subsets import vector_from_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_c5_calibration_must_pass():
    # Rays 1-9 are VERIFICATION: their published models are simple trees, so
    # chordality must hold — a failure here is an implementation bug.
    for k in range(1, 10):
        r = simple_forest_realizable(vector_from_paper(C5_EXTREME_RAYS[k - 1], 5), 5)
        assert r["chordal"], f"ray {k} must be chordal (known simple tree)"


def test_c5_rays_10_19_derived_facts():
    # Rays 10-19 non-chordal is a DERIVED FACT (new, criterion-dependent),
    # not verification: no prior source proves they lack simple-tree models.
    # It is consistent with the literature (2204.00075 needed non-simple
    # trees for exactly the non-tree-realized rays) and with every cyclic
    # model our engines found. Locked as regression.
    for k in range(10, 20):
        r = simple_forest_realizable(vector_from_paper(C5_EXTREME_RAYS[k - 1], 5), 5)
        assert not r["chordal"], f"ray {k} expected non-chordal (derived fact)"


def test_tree_builder_end_to_end():
    # Constructive direction: chordal vectors must yield verified forests.
    import networkx as nx

    from hec.entropy import entropy_vector
    from hec.tree_builder import build_simple_forest

    for k in range(1, 10):
        S = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
        G = build_simple_forest(S, 5)
        assert nx.is_forest(G)
        assert entropy_vector(G, 5) == S


def test_mystery_orbits_all_fail_chordality():
    targets = json.loads((ROOT / "data/targets/mystery_orbits.json").read_text())
    for s, vec in targets["orbits"].items():
        r = simple_forest_realizable(vector_from_paper(tuple(vec), 6), 6)
        assert r["chordal"] is False, f"orbit {s}"

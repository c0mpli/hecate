"""Chordality criterion: locked to the 19-ray ground truth + the gate result."""

import json
import pathlib

from hec.c5_data import C5_EXTREME_RAYS
from hec.chordality import simple_forest_realizable
from hec.subsets import vector_from_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_c5_calibration():
    # rays 1-9: published models are simple trees; 10-19: provably not
    for k, ray in enumerate(C5_EXTREME_RAYS, start=1):
        r = simple_forest_realizable(vector_from_paper(ray, 5), 5)
        assert r["chordal"] == (k <= 9), f"ray {k}"


def test_mystery_orbits_all_fail_chordality():
    targets = json.loads((ROOT / "data/targets/mystery_orbits.json").read_text())
    for s, vec in targets["orbits"].items():
        r = simple_forest_realizable(vector_from_paper(tuple(vec), 6), 6)
        assert r["chordal"] is False, f"orbit {s}"

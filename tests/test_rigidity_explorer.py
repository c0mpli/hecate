"""rigidity_explorer — soundness regressions for the hypothesis-generating
experiment. The critical invariant: the 'cycle_surgery_fixed_point' feature is a
SOUND encoding of the session-9 dead-end signature — it must fire on a genuine
dead end and NEVER on a graph that still has a move (a false positive there
would silently claim rigidity that does not exist). Plus: labels are sound on
the positive side (known-breakable C5 seeds), and exactness of the features."""

import json
from fractions import Fraction

import networkx as nx

from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.rigidity_explorer import (
    _is_cycle_surgery_fixed_point,
    calibrate_known_breakable,
    graph_features,
    label_case,
    random_cyclic_graph,
    validate_detector,
)


def test_detector_self_check_passes():
    """The dead-end detector must fire True on a genuine session-9 dead end and
    False on a moveable graph (a bulk triangle). This is the soundness gate."""
    v = validate_detector()
    assert v["dead_end_detected"] is True
    assert v["moveable_rejected"] is True
    assert v["ok"] is True


def test_s111_seed_is_not_a_dead_end():
    """The published s=111 cyclic seed is a Δ→Y SEARCH START, not a dead end:
    the fixed-point feature must report False on it. (A True here would mean we
    mistake a reducible seed for a genuine dead end — the exact error that would
    let 'rigid' masquerade as structural.)"""
    def _norm(x):
        return int(x) if isinstance(x, str) and x in ("0", "1", "2", "3", "4", "5") else x
    seeds = json.loads(
        (__import__("pathlib").Path(__file__).resolve().parent.parent
         / "data" / "targets" / "bulk_cycle_seeds.json").read_text())["seeds"]
    if "111" not in seeds:
        return  # seed file optional; skip if absent
    G = nx.Graph()
    party = {}
    for lab in list(range(6)) + ["O"]:
        G.add_node(lab)
        party[lab] = lab
    for u, v, w in seeds["111"]["edges"]:
        G.add_edge(_norm(u), _norm(v), capacity=Fraction(int(w)))
    assert _is_cycle_surgery_fixed_point(G, party, 6) is False


def test_fixed_point_never_fires_on_a_breakable_case():
    """Soundness invariant on real data: if a graph is a fixed point, no move
    applies, so cycle_surgery cannot break it — hence a fixed point can NEVER be
    breakable. Verify on a handful of generated breakable cases."""
    import random
    rng = random.Random(7)
    checked = 0
    for _ in range(40):
        gp = random_cyclic_graph(5, rng, "boundary", rng.randint(1, 3))
        if gp is None:
            continue
        G, party = gp
        label, _ = label_case(G, party, 5)
        if label == "breakable":
            assert graph_features(G, party, 5)["cycle_surgery_fixed_point"] == 0
            checked += 1
        if checked >= 5:
            break
    assert checked >= 1, "expected at least one breakable case to check"


def test_features_are_exact_integers():
    """All structural features must be exact ints (no floats in labels/features
    — floats are only allowed in the downstream stump ranking)."""
    import random
    rng = random.Random(3)
    gp = random_cyclic_graph(6, rng, "bulk", 3)
    assert gp is not None
    G, party = gp
    feats = graph_features(G, party, 6)
    expected = {"cyclomatic", "n_bulk_cycles", "max_bulk_cycle_len",
                "n_bulk_triangles", "n_deg3_bulk", "max_bulk_degree",
                "cycle_surgery_fixed_point"}
    assert expected <= set(feats)
    for k, val in feats.items():
        assert isinstance(val, int), f"{k}={val!r} is not an int"


def test_known_breakable_c5_calibration():
    """Positive-side label calibration: the published C5 seeds for rays 10 and
    17 are tree-realizable (cracked in prior sessions), so they MUST label
    breakable. Guards against a regression that mislabels realizable cases."""
    out = calibrate_known_breakable()
    assert out["c5_ray_10"] == "breakable"
    assert out["c5_ray_17"] == "breakable"
    assert out["ok"] is True

"""two_split_enumerator — soundness + the binding gates A/B/C.

The tool's worth is a TRUSTWORTHY answer to the exactly-2-split tree question for
s=111. These tests pin: (i) the split-structure space is exactly what it claims
(distinct, exactly-k labels split); (ii) the gates pass (lift correct, fit
recovers KNOWN trees so a negative is not a false negative, coarse-grain
round-trips exactly); (iii) only BOUNDED negatives are ever emitted (no
"non-realizable"/"no tree exists"/"proven rigid" in the source or qualifiers).
The full s=111 sweep is too slow for CI and runs as `python -m
hec.two_split_enumerator`; its result is recorded in NOTES + reports."""

import pathlib

from hec.two_split_enumerator import (
    LABELS,
    decide_k_split,
    gate_a,
    gate_b,
    gate_b_3split,
    gate_c,
    k_split_structures,
)


def test_k_split_structures_exactly_k_and_distinct():
    """Exactly-k-split space: choose k of the n+1 boundary objects, each into
    [2,m_max]; the rest single. Counts and the exactly-k property must hold."""
    s2 = k_split_structures(6, 2, 2)
    assert len(s2) == 21, "C(7,2) = 21 two-split structures for n=6, m_max=2"
    for mult, split_labels in s2:
        assert len(split_labels) == 2
        assert all(mult[l] == 2 for l in split_labels)
        assert sum(1 for l in LABELS(6) if mult[l] > 1) == 2  # EXACTLY two split
        assert all(mult[l] == 1 for l in LABELS(6) if l not in split_labels)
    # distinct
    keys = {tuple(sorted((str(k), v) for k, v in m.items())) for m, _ in s2}
    assert len(keys) == 21
    # 1-split (gate A space) and m_max=3 widening
    assert len(k_split_structures(5, 1, 2)) == 6
    assert len(k_split_structures(6, 2, 3)) == 21 * 4  # each split in {2,3}


def test_gate_c_round_trip_exact():
    """Lifting round-trip: a refined tree's vector coarse-grains EXACTLY back to
    the labeled vector it realizes, and the refined tree is chordal."""
    C = gate_c(log=lambda m: None)
    assert C["ok"] is True
    assert C["round_trip_exact"] is True
    assert C["refined_chordal"] is True


def test_gate_a_one_split_lift_and_fit():
    """GATE A: the known 1-split tree for ray 11 certifies through the lift
    pipeline and the fitter recovers it from its bare topology."""
    A = gate_a(log=lambda m: None)
    assert A["certify_lift"] is True
    assert A["refit_recovers"] is True
    assert A["ok"] is True
    assert A["n_splits"] == 1


def test_gate_b_known_trees_recovered_no_false_negative():
    """GATE B: rays 10/17 are tree-realizable; their KNOWN trees (3 splits) must
    certify + be recovered by the fitter. A miss would be a false negative that
    invalidates an s=111 negative."""
    B = gate_b(log=lambda m: None)
    assert B["ok"] is True
    for k in (10, 17):
        assert B["cases"][k]["ok"] is True
        assert B["cases"][k]["n_splits"] == 3  # known trees are 3-split (measured)


def test_negative_is_bounded_and_never_unbounded():
    """A no-tree result on a tiny restricted search must be a BOUNDED negative
    whose qualifier carries the bound and NONE of the forbidden unbounded
    phrases."""
    # ray 11 restricted to splitting party 0 only, n_bulk=1 (a 1-tree cell):
    from hec.c5_data import C5_EXTREME_RAYS
    cert, info = decide_k_split("c5_11_tiny", C5_EXTREME_RAYS[10], 5, k=1, m_max=2,
                                n_bulk_range=range(1, 2), split_filter={0},
                                fit_attempts=1, fit_descents=8, out_dir=None,
                                log=lambda m: None)
    assert info["status"] in ("no_tree_found", "tree")
    if info["status"] == "no_tree_found":
        q = info["qualifier"].lower()
        assert "bounded" in q
        for forbidden in ("non-realizable", "no tree exists", "proven rigid",
                          "not realizable"):
            assert forbidden not in q


def test_source_has_no_unbounded_nonexistence_claims():
    """Grep gate: the module source must never assert non-realizability except
    inside an explicit disclaimer. Mirrors the repo discipline."""
    src = (pathlib.Path(__file__).resolve().parent.parent / "hec" /
           "two_split_enumerator.py").read_text().lower()
    disclaimers = ("not", "never", "no proof", "n't", "carry no", "without",
                   "avoid", 'no "', "only the bounded")
    for phrase in ("no tree exists", "non-realizable", "proven rigid"):
        idx = 0
        while True:
            idx = src.find(phrase, idx)
            if idx == -1:
                break
            window = src[max(0, idx - 60):idx]
            assert any(d in window for d in disclaimers), \
                f"bare '{phrase}' near: ...{src[idx - 60:idx + 20]}"
            idx += len(phrase)


def test_k3_split_structures_count():
    """Exactly-3-split space: C(7,3)=35 triples for n=6, m_max=2; exactly three
    labels split, each into 2."""
    s3 = k_split_structures(6, 3, 2)
    assert len(s3) == 35
    for mult, labels in s3:
        assert len(labels) == 3
        assert sum(1 for l in LABELS(6) if mult[l] > 1) == 3
        assert all(mult[l] == 2 for l in labels)


def test_k3_decide_checkpoint_and_partial_label():
    """The k=3 path emits checkpoints and a cap-truncated cell is labeled PARTIAL
    (never a completed negative). Tiny restricted search (one triple, n_bulk=4,
    small cap) keeps it fast."""
    from hec.c5_data import C5_EXTREME_RAYS  # noqa: F401 (import-time sanity)
    import json
    v111 = json.loads((__import__("pathlib").Path(__file__).resolve().parent.parent
                       / "data" / "targets" / "bulk_cycle_orbits.json").read_text())["orbits"]["111"]
    fired = []
    cert, info = decide_k_split("111", v111, 6, k=3, m_max=2, n_bulk_range=[4],
                                fit_attempts=1, fit_descents=6, fit_cut_rounds=6,
                                max_trees=12, time_budget=120, split_filter={0, 1, 2},
                                out_dir=None, log=lambda m: None,
                                checkpoint=lambda pi: fired.append(pi["distinct_structures_tested"]),
                                checkpoint_every=5)
    if cert is None:
        assert info["caps_hit"]["candidate_cap_truncated"] is True
        assert "PARTIAL" in info["qualifier"]
        assert "not a proof" in info["qualifier"].lower()
    assert fired and fired[0] == 5  # checkpoint fired at the cadence


def test_gate_b_3split_recovers_known_trees():
    """GATE B (3-split): the sweep-strength fit (a=4) recovers rays 10/17 KNOWN
    3-split trees — the credibility gate for any 111/207 negative."""
    B = gate_b_3split(log=lambda m: None)
    assert B["ok"] is True
    for k in (10, 17):
        assert B["cases"][k]["ok"] is True
        assert B["cases"][k]["n_splits"] == 3
        assert B["cases"][k]["n_bulk"] == 4  # known 3-split trees live at n_bulk=4


def test_bounded_negative_qualifier_is_clean():
    """The runtime CLAIM (the qualifier of a bounded negative) is where an
    unsound non-existence statement would do damage — assert it is bounded and
    free of affirmative non-existence language."""
    from hec.c5_data import C5_EXTREME_RAYS
    _, info = decide_k_split("c5_11_tiny2", C5_EXTREME_RAYS[10], 5, k=1, m_max=2,
                             n_bulk_range=range(1, 2), split_filter={1},
                             fit_attempts=1, fit_descents=8, out_dir=None,
                             log=lambda m: None)
    if info["status"] == "no_tree_found":
        q = info["qualifier"].lower()
        assert "bounded" in q and "not a proof" in q
        for bad in ("no tree exists", "non-realizable", "proven rigid",
                    "not realizable", "no realization exists"):
            assert bad not in q

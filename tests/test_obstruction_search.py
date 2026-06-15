"""Guards for hec.obstruction_search — the cheap LP-free obstruction test.

The experiment's integrity rests on a few facts that must not silently drift:
the reference-set reconstruction (148 + 19), the chordality census that makes
the control meaningful (chordality is a TRAP — it flags tree-realizable rays),
the soundness of the optimised 4-hole count, and the headline verdict (no cheap
invariant separates s=111; the 10/17 controls are never flagged).
"""
import itertools

import networkx as nx
import pytest

from hec.c5_data import C5_EXTREME_RAYS
from hec.chordality import correlation_hypergraph, line_graph
from hec.obstruction_search import (
    count_induced_4holes,
    reference_set,
    run,
    tree_realizable_indices,
)
from hec.subsets import vector_from_paper


@pytest.fixture(scope="module")
def R():
    return run()


def test_reference_set_sizes():
    assert len(tree_realizable_indices()) == 148
    recs = reference_set()
    n6 = [r for r in recs if r["n"] == 6 and r["role"] == "tree-realizable"]
    c5 = [r for r in recs if r["n"] == 5]
    targets = [r for r in recs if r["role"] == "target"]
    controls = [r for r in recs if r["role"] == "control"]
    assert len(n6) == 148
    assert len(c5) == 19                       # all 19 C5 orbits are tree-realizable
    assert {r["name"] for r in targets} == {"n6:111", "n6:207"}
    assert {r["name"] for r in controls} == {"c5:10", "c5:17"}


def test_chordality_census_is_the_control_spine(R):
    # 104 of the 148 tree-realizable n=6 orbits are THEMSELVES non-chordal:
    # chordality therefore certifies "has a bulk cycle", not non-realizability.
    assert R["n6_chordal"] == 44
    assert R["n6_nonchordal"] == 104
    assert R["n6_chordal"] + R["n6_nonchordal"] == 148


def test_chordality_is_a_trap_not_an_obstruction(R):
    # The chordality invariant "separates" 111 from the chordal trees, but it
    # FLAGS both tree-realizable controls (10/17 are non-chordal) -> it fails the
    # control and is not a valid obstruction. Encoded so a regression that
    # promoted chordality to a "separator" would fail loudly.
    chordal = R["results"]["chordal"]
    assert chordal["control_c5_10"] == 0 and chordal["control_c5_17"] == 0
    assert "chordal" not in R["separators"]["111"]


def test_no_invariant_flags_the_controls(R):
    # Control check: for every n-agnostic invariant (the only ones comparable to
    # the n=5 controls), rays 10 and 17 lie INSIDE the cohort range. No
    # n-agnostic invariant flags a known tree-realizable ray.
    for key, v in R["results"].items():
        if v["control_inside"] is not None:
            assert v["control_inside"] is True, f"{key} flags a control"


def test_headline_s111_has_no_separator(R):
    # The primary result: no non-degenerate invariant separates s=111 from the
    # non-chordal tree-realizable cohort.
    assert R["separators"]["111"] == []
    # ... and 111 is strictly INTERIOR (never at a 0/100 percentile edge) on the
    # discriminating same-n invariants — "ordinary", not a boundary case.
    pcts = [v["targets"]["111"]["percentile"]
            for v in R["results"].values() if not v["n6_constant"]]
    assert pcts and all(0 < p < 100 for p in pcts)


def test_s111_inside_every_cohort_range(R):
    for key, v in R["results"].items():
        t = v["targets"]["111"]
        assert v["cohort_min"] <= t["value"] <= v["cohort_max"], key
        assert t["separates"] is False, key


def test_targets_excluded_from_cohort(R):
    # cohort_size must be the 104 non-chordal n=6 trees (+10 C5 for n-agnostic);
    # never the targets themselves.
    for key, v in R["results"].items():
        assert v["cohort_size"] in (104, 114), key


def test_fast_4hole_count_matches_brute_force():
    def brute(L):
        nodes = list(L.nodes)
        c = 0
        for sub in itertools.combinations(nodes, 4):
            H = L.subgraph(sub)
            if (H.number_of_edges() == 4
                    and all(d == 2 for _, d in H.degree())
                    and nx.is_connected(H)):
                c += 1
        return c

    for k in (10, 11, 17, 19):                 # non-chordal C5 rays (small line graphs)
        S = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
        L = line_graph(correlation_hypergraph(S, 5))
        assert count_induced_4holes(L) == brute(L), f"C5 ray {k}"

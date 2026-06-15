"""Guards for hec.attack_207 — the s=207 bulk-cycle attack.

The most important guard is the s181 lesson: the seed must EXACTLY realize the
s=207 ray, or every downstream result is meaningless. The rest pin the
characterization (genuine bulk-cycle case, pure-bulk 4-cycle core) and the
STEP-2 outcome (a bounded negative, the same obstruction class as 111).
"""
import pytest

from hec.attack_207 import (
    build_seed,
    characterize_seed,
    compare,
    rep_207,
    validate_seed,
)
from hec.entropy import entropy_vector_labeled
from hec.subsets import vector_to_paper


def test_seed_realizes_207_exactly():
    # s181 lesson: confirm the realization, never assume it.
    G, party = build_seed()
    S = entropy_vector_labeled(G, 6, party)
    paper = vector_to_paper(S, 6)
    rep = rep_207()
    scale = next((k for k in range(1, 40)
                  if all(paper[i] == k * rep[i] for i in range(63))), None)
    assert scale == 2, "seed must exactly realize 2x the s=207 representative"


@pytest.fixture(scope="module")
def val():
    return validate_seed(log=lambda m: None)


def test_seed_is_the_bulk_cycle_case(val):
    assert val["seed_realizes_207_exact"] is True
    assert val["SA_SSA"] is True
    assert val["SAC_extreme"] is True and val["saturated_SA_rank"] == 62
    assert val["HEI_clean"] is True          # genuinely holographic
    assert val["non_chordal"] is True        # surviving bulk cycle


def test_seed_core_is_a_pure_bulk_4cycle():
    G, party = build_seed()
    ch = characterize_seed(G, party)
    assert ch["cyclomatic"] == 4             # bulk 4-cycle + 3 boundary triangles
    assert ch["n_pure_bulk_cycles"] == 1
    pb = ch["pure_bulk_cycle"]
    assert pb["length"] == 4
    assert sorted(pb["degrees"].values()) == [4, 4, 5, 5]
    assert pb["delta_y_applicable"] is False  # no triangle on the bulk cycle


@pytest.fixture(scope="module")
def comparison():
    cmp, _, _ = compare(log=lambda m: None)
    return cmp


def test_surgery_is_a_bounded_negative(comparison):
    # 207 stalls — surgery returns a bounded no_reduction, not a tree.
    assert comparison["207"]["surgery"] == "no_reduction"


def test_207_same_obstruction_class_as_111(comparison):
    # The payoff contrast: both twins bottom out on a pure-bulk 4-cycle.
    assert comparison["same_obstruction_class"] is True
    assert comparison["111"]["surgery"] == "no_reduction"
    for s in ("111", "207"):
        core = comparison[s]["pure_bulk_core"]
        assert core is not None and core["length"] == 4

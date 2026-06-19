"""dual_search — the vacuity reductio, pinned as a regression.

The point of hec/dual_search.py is to PROVE (not just suspect) that the naive
sample-separation route to s=111 non-tree-realizability is geometrically vacuous:
it "certifies" KNOWN tree-realizable extreme rays as non-realizable at the same
100% rate as s=111. These tests pin that demonstration and the claim discipline
(no rigidity/non-realizability claim about s=111 anywhere)."""

import pathlib

import numpy as np

from hec.c5_data import C5_EXTREME_RAYS
from hec.dual_search import _separable, demonstrate_vacuity, tree_boundary_summary


def test_known_realizable_vector_is_separated_extremality_artifact():
    """A KNOWN tree-realizable extreme ray (C5 ray 10) IS separable from the other
    tree-realizable rays — the exact false-positive a sound method must never
    produce. This is the extremality artifact, witnessed directly."""
    c5 = [np.array(v, float) for v in C5_EXTREME_RAYS]
    assert _separable(c5[9], c5[:9] + c5[10:]) is True  # ray 10, known realizable


def test_vacuity_is_total():
    """The reductio: 19/19 + 148/148 KNOWN tree-realizable rays separated, and
    s=111/207 separated at the same rate. A method that 'proves' every known-
    realizable ray non-realizable proves nothing about s=111."""
    vac = demonstrate_vacuity(log=lambda m: None)
    assert vac["n5_known_realizable_separated"] == "19/19"
    assert vac["n5_controls_10_17_separated"] == {10: True, 17: True}
    assert vac["n6_known_realizable_separated"] == "148/148"
    assert vac["targets_separated"] == {"111": True, "207": True}


def test_reframe_names_the_combinatorial_boundary():
    """The reframe must state that the tree-region boundary is combinatorial
    (chordality / fine-graining), not a known set of linear facets."""
    s = tree_boundary_summary()
    assert "NO finite set of linear facets" in s["tree_region_facets"]
    assert "chordality iff" in s["simple_tree_boundary"]
    assert "fine-graining" in s["non_simple_tree_boundary"]


def test_no_affirmative_rigidity_claims():
    """Claim discipline: NO affirmative construction asserting s=111 is non-
    realizable/rigid/proven appears; and the module explicitly disclaims, calling
    the dual route vacuous and the tree question open."""
    src = (pathlib.Path(__file__).resolve().parent.parent / "hec" /
           "dual_search.py").read_text().lower()
    affirmative = [
        "s=111 is non-realizable", "s=111 is rigid", "111 is rigid",
        "s=111 is not tree", "111 is not tree-realizable",
        "proven non-realizable", "proves s=111 is", "s=111 is proven",
        "rigidity of s=111 is established",
    ]
    for bad in affirmative:
        assert bad not in src, f"affirmative rigidity claim present: {bad!r}"
    # and it must loudly disclaim
    assert "vacuous" in src
    assert "open" in src
    assert "cannot" in src

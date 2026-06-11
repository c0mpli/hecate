"""Engine tests against hand-computed S-vectors (the M0 acceptance exercise).

Bitmask convention for n=3: A=1, B=2, AB=3, C=4, AC=5, BC=6, ABC=7.
"""

import random

import networkx as nx
import pytest

from hec.entropy import PURIFIER, entropy_vector, subset_label
from hec.graphs import random_mixture
from hec.inequalities import check_vector

A, B, AB, C, AC, BC, ABC = 1, 2, 3, 4, 5, 6, 7


def star(wa, wb, wc, wo):
    G = nx.Graph()
    for v, w in [(0, wa), (1, wb), (2, wc), (PURIFIER, wo)]:
        G.add_edge("b0", v, capacity=w)
    return G


def test_star_hand_computed():
    # Star with center bulk vertex, weights a,b,c,o. A cut either isolates
    # the chosen parties' legs or takes the complementary legs (center side
    # flips), so e.g. S(A) = min(a, b+c+o), S(AB) = min(a+b, c+o).
    S = entropy_vector(star(3, 1, 2, 4), 3)
    assert S == {
        A: 3,      # min(3, 1+2+4)
        B: 1,      # min(1, 3+2+4)
        C: 2,      # min(2, 3+1+4)
        AB: 4,     # min(3+1, 2+4)
        AC: 5,     # min(3+2, 1+4)
        BC: 3,     # min(1+2, 3+4)
        ABC: 4,    # min(3+1+2, 4)
    }
    assert check_vector(S, 3) == []


def test_star_uniform():
    S = entropy_vector(star(1, 1, 1, 1), 3)
    assert S == {A: 1, B: 1, C: 1, AB: 2, AC: 2, BC: 2, ABC: 1}
    assert check_vector(S, 3) == []


def test_cycle_hand_computed():
    # 4-cycle A-B-O-C-A, all vertices on the boundary (no bulk freedom):
    # every cut is forced, e.g. S(BC) must cut all four edges.
    G = nx.Graph()
    G.add_edge(0, 1, capacity=1)         # A-B
    G.add_edge(1, PURIFIER, capacity=2)  # B-O
    G.add_edge(PURIFIER, 2, capacity=3)  # O-C
    G.add_edge(2, 0, capacity=4)         # C-A
    S = entropy_vector(G, 3)
    assert S == {A: 5, B: 3, C: 7, AB: 6, AC: 4, BC: 10, ABC: 5}
    # This vector saturates MMI: 6+4+10 == 5+3+7+5.
    assert check_vector(S, 3) == []


def test_parallel_edges_and_self_loops():
    G = nx.MultiGraph()
    G.add_edge(0, "b0", capacity=2)
    G.add_edge(0, "b0", capacity=3)      # parallel: merges to 5
    G.add_edge("b0", "b0", capacity=99)  # self-loop: ignored
    for v in [1, 2, PURIFIER]:
        G.add_edge("b0", v, capacity=10)
    S = entropy_vector(G, 3)
    assert S[A] == 5


def test_missing_boundary_raises():
    G = nx.Graph()
    G.add_edge(0, 1, capacity=1)
    with pytest.raises(ValueError):
        entropy_vector(G, 3)


def test_subset_label():
    assert subset_label(0b101, 3) == "AC"
    assert subset_label(0b111111, 6) == "ABCDEF"


def test_random_graphs_satisfy_all_inequalities():
    # Smoke-scale version of scripts/day1_mmi.py (which runs 10k+).
    rng = random.Random(7)
    for _ in range(200):
        G = random_mixture(3, rng)
        S = entropy_vector(G, 3)
        assert check_vector(S, 3) == []
        assert all(isinstance(s, int) for s in S.values())  # exactness

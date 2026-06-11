"""Contraction-map prover tests."""

from hec.prover import (
    Inequality,
    check_contraction,
    find_contraction_bruteforce,
    find_contraction_cpsat,
)

MMI = Inequality(
    "MMI", {"AB": 1, "AC": 1, "BC": 1}, {"A": 1, "B": 1, "C": 1, "ABC": 1}, 3
)


def test_mmi_bruteforce():
    f = find_contraction_bruteforce(MMI)
    assert f is not None
    assert check_contraction(MMI, f) == []


def test_checker_rejects_bad_map():
    f = find_contraction_bruteforce(MMI)
    # corrupt a boundary image: x_A = (1,1,0) must map to y_A = (1,0,0,1)
    f[(1, 1, 0)] = (0, 0, 0, 0)
    assert any("(C1)" in e for e in check_contraction(MMI, f))


def test_checker_rejects_non_lipschitz():
    f = find_contraction_bruteforce(MMI)
    # send a free point far away: distance to f((0,0,0)) = (0,0,0,0) becomes 3 > 1
    f[(1, 0, 0)] = (1, 1, 1, 0)
    assert any("(C2)" in e for e in check_contraction(MMI, f))


def test_false_inequality_has_no_map():
    # S(A) + S(B) >= S(A) + S(B) + S(AB) is false; no contraction map exists
    bogus = Inequality("bogus", {"A": 1, "B": 1}, {"A": 1, "B": 1, "AB": 1}, 2)
    assert find_contraction_bruteforce(bogus) is None
    assert find_contraction_cpsat(bogus, time_limit_s=10) is None


def test_cpsat_proves_qcyclic():
    q = Inequality(
        "QCyclic",
        {"ABC": 1, "ABD": 1, "ACE": 1, "BDE": 1, "CDE": 1},
        {"AB": 1, "AC": 1, "BD": 1, "CE": 1, "DE": 1, "ABCDE": 1},
        5,
    )
    f = find_contraction_cpsat(q, time_limit_s=60)
    assert f is not None and check_contraction(q, f) == []

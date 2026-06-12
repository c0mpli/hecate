"""5-party cone regression (the fast core of scripts/verify_c5.py)."""

from hec.c5_data import (
    C5_EXTREME_RAYS,
    C5_INEQUALITIES,
    EXPECTED_FACET_ORBIT_SIZES,
    TOTAL_EXTREME_RAYS,
    TOTAL_FACETS,
)
from hec.cone import (
    expand_inequalities,
    in_cone,
    is_extreme_ray,
    orbit,
    sa_instances,
    ssa_instances,
)
from hec.subsets import vector_from_paper


def test_facet_orbits_and_ray_extremality():
    facets, sizes = expand_inequalities(C5_INEQUALITIES, 5)
    assert sizes == EXPECTED_FACET_ORBIT_SIZES
    assert len(facets) == TOTAL_FACETS
    for ray in C5_EXTREME_RAYS:
        assert in_cone(ray, facets)
        assert is_extreme_ray(ray, facets, 5)


def test_ray_orbit_sizes_sum_to_2267():
    total = sum(
        len(orbit(vector_from_paper(r, 5), 5)) for r in C5_EXTREME_RAYS
    )
    assert total == TOTAL_EXTREME_RAYS


def test_instance_family_sizes():
    # locked-in counts for the full polychromatic families (n=6: SAC facets);
    # SA count = ((3^(n+1) - 2^(n+2) + 1) - (2^(n+1) - 2)) / 2
    assert len(sa_instances(6)) == 903
    assert len(ssa_instances(6)) == 3003
    assert len(sa_instances(3)) == 18

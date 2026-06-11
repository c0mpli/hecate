"""Polyhedral-cone tools: Sym(n+1) symmetry action, membership, extremality.

Entropy space for n parties is R^(2^n - 1). The symmetry group of the
problem is Sym(n+1): all permutations of the n parties *and* the purifier O.
Its action uses purity, S(I) = S(I^c), where the complement is taken inside
the full set of n+1 boundary labels: a permuted subset that contains O is
replaced by its complement, which doesn't. Both entropy vectors and
inequality functionals (stored over party subsets only) transform by this
push-forward.

Everything here is exact: integer/Fraction arithmetic, sympy ranks.
"""

from __future__ import annotations

from itertools import permutations

import sympy

from hec.subsets import mask_of_label, vector_to_paper


def ineq_to_coeffs(lhs: dict[str, int], rhs: dict[str, int], n: int) -> dict[int, int]:
    """LHS >= RHS  ->  {mask: coeff} with  sum coeff * S >= 0."""
    v = {m: 0 for m in range(1, 1 << n)}
    for label, c in lhs.items():
        v[mask_of_label(label)] += c
    for label, c in rhs.items():
        v[mask_of_label(label)] -= c
    return v


def permute_vector(v: dict[int, int], perm: tuple[int, ...], n: int) -> dict[int, int]:
    """Push v forward along a permutation of the n+1 labels (O = label n)."""
    full = (1 << n) - 1
    out = {}
    for m, val in v.items():
        img = 0
        has_o = False
        for i in range(n):
            if m >> i & 1:
                p = perm[i]
                if p == n:
                    has_o = True
                else:
                    img |= 1 << p
        if has_o:
            img = full & ~img  # purity: replace by complement without O
        out[img] = val
    return out


def orbit(v: dict[int, int], n: int) -> set[tuple]:
    """All distinct Sym(n+1) images of v, as paper-order tuples."""
    seen = set()
    for perm in permutations(range(n + 1)):
        seen.add(vector_to_paper(permute_vector(v, perm, n), n))
    return seen


def canonical_vector(v: dict[int, int], n: int) -> tuple:
    """Orbit representative: lexicographic minimum over Sym(n+1) images."""
    return min(orbit(v, n))


def dot(f: tuple, v: tuple) -> int:
    return sum(a * b for a, b in zip(f, v))


def in_cone(v: tuple, facets: list[tuple]) -> bool:
    return all(dot(f, v) >= 0 for f in facets)


def saturated_facets(v: tuple, facets: list[tuple]) -> list[tuple]:
    return [f for f in facets if dot(f, v) == 0]


def is_extreme_ray(v: tuple, facets: list[tuple], n: int) -> bool:
    """v generates an extreme ray of the cone {S : f.S >= 0 for all facets}.

    Criterion: v != 0, v in the cone, and the facets tight at v span a
    hyperplane — rank 2^n - 2 — so the face containing v is 1-dimensional.
    """
    if not any(v) or not in_cone(v, facets):
        return False
    sat = saturated_facets(v, facets)
    if not sat:
        return False
    return sympy.Matrix(sat).rank() == (1 << n) - 2


def _reduce(J: int, n: int) -> int:
    """7-label mask -> party mask via purity (label n is the purifier)."""
    if J >> n & 1:
        J = ~J & ((1 << (n + 1)) - 1)
    return J


def sa_instances(n: int) -> list[tuple]:
    """ALL subadditivity instances S(I)+S(J) >= S(IJ), I,J disjoint nonempty
    subsets of the n+1 boundary labels with IJ proper. This is the facet set
    of the subadditivity cone (SAC); it includes Araki-Lieb via purity. The
    polychromatic instances are NOT in the Sym(n+1) orbit of S(A)+S(B)>=S(AB),
    which is why this is its own constructor."""
    full = (1 << (n + 1)) - 1
    out = set()
    for I in range(1, full + 1):
        for J in range(1, full + 1):
            if I & J or J <= I or (I | J) == full:
                continue
            f = {m: 0 for m in range(1, 1 << n)}
            f[_reduce(I, n)] += 1
            f[_reduce(J, n)] += 1
            f[_reduce(I | J, n)] -= 1
            out.add(vector_to_paper(f, n))
    return sorted(out)


def ssa_instances(n: int) -> list[tuple]:
    """ALL strong-subadditivity instances S(XY)+S(YZ) >= S(Y)+S(XYZ) over
    disjoint nonempty subsets X, Y, Z of the n+1 boundary labels (weak
    monotonicity is included via purity; X|Y|Z may cover everything, in
    which case the S(XYZ) term vanishes)."""
    full = (1 << (n + 1)) - 1
    out = set()
    for Y in range(1, full + 1):
        rest = full & ~Y
        for X in range(1, full + 1):
            if X & ~rest:
                continue
            for Z in range(1, full + 1):
                if Z <= X or Z & ~rest or Z & X:
                    continue
                f = {m: 0 for m in range(1, 1 << n)}
                f[_reduce(X | Y, n)] += 1
                f[_reduce(Y | Z, n)] += 1
                f[_reduce(Y, n)] -= 1
                xyz = X | Y | Z
                if xyz != full:
                    f[_reduce(xyz, n)] -= 1
                out.add(vector_to_paper(f, n))
    return sorted(out)


def perm_index_matrix(n: int):
    """All Sym(n+1) actions as index maps on paper-order positions.

    Row p is a length-(2^n - 1) array sigma with (perm_p . v)[k] = v[sigma[k]]
    for any paper-order vector v — the purified symmetry action is a pure
    permutation of components. Lets numpy apply the whole group at once:
    images = v[PERM] is a (n+1)!-row matrix of all images of v.
    """
    from hec.subsets import paper_order

    order = paper_order(n)
    pos = {m: i for i, m in enumerate(order)}
    ident = {m: pos[m] for m in order}  # value = source position
    rows = []
    for perm in permutations(range(n + 1)):
        moved = permute_vector(ident, perm, n)
        rows.append([moved[m] for m in order])
    return rows


def expand_inequalities(named_ineqs, n: int):
    """[(name, lhs, rhs)] -> (instances, orbit_sizes); instances deduped."""
    instances: set[tuple] = set()
    sizes = []
    for _name, lhs, rhs in named_ineqs:
        o = orbit(ineq_to_coeffs(lhs, rhs, n), n)
        sizes.append(len(o))
        instances |= o
    return sorted(instances), sizes

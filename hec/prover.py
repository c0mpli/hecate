"""Contraction-map proofs of holographic entropy inequalities.

The proof method of BNOSSW (arXiv:1505.07839 §3), complete for rational
inequalities by arXiv:2506.18086. To prove

    sum_l alpha_l S(I_l)  >=  sum_r beta_r S(J_r),   alpha, beta > 0,

attach to every boundary label i (parties and the purifier O) its occurrence
vectors x_i in {0,1}^L, (x_i)_l = [i in I_l], and y_i in {0,1}^R. A
*contraction map* is f: {0,1}^L -> {0,1}^R with

  (C1)  f(x_i) = y_i for every boundary label i  (note x_O = 0, y_O = 0),
  (C2)  d_beta(f(x), f(x')) <= d_alpha(x, x') for all x, x' in {0,1}^L,

where d_w(u, v) = sum_k w_k |u_k - v_k| is the weighted Hamming distance.
If f exists the inequality holds on every graph model, hence on the whole
holographic entropy cone: given minimal cuts for the LHS terms, each vertex
v inherits a bitstring x(v) of cut memberships; the sets {v : f(x(v))_r = 1}
are valid (not necessarily minimal) cuts for the RHS terms, and (C2) bounds
their total beta-weighted capacity by the alpha-weighted LHS, edge by edge.

Since d_alpha is the path metric of the alpha-weighted hypercube, (C2) for
single-bit flips implies (C2) in general; the searchers exploit this, the
checker still verifies every pair.
"""

from __future__ import annotations

from itertools import product

from hec.entropy import subset_label
from hec.subsets import mask_of_label


class Inequality:
    """sum alpha_l S(I_l) >= sum beta_r S(J_r) over n parties (masks)."""

    def __init__(self, name: str, lhs, rhs, n: int):
        self.name = name
        self.n = n
        self.lhs = [(int(c), mask_of_label(s) if isinstance(s, str) else s) for s, c in lhs.items()]
        self.rhs = [(int(c), mask_of_label(s) if isinstance(s, str) else s) for s, c in rhs.items()]
        if any(c <= 0 for c, _ in self.lhs + self.rhs):
            raise ValueError("contraction method needs strictly positive coefficients")
        self.alpha = [c for c, _ in self.lhs]
        self.beta = [c for c, _ in self.rhs]
        self.L = len(self.lhs)
        self.R = len(self.rhs)

    def occurrence_vectors(self):
        """(x_i, y_i) for each boundary label i = 0..n (label n is O)."""
        xs, ys = {}, {}
        for i in range(self.n + 1):
            bit = 0 if i == self.n else (1 << i)
            xs[i] = tuple(1 if m & bit else 0 for _, m in self.lhs)
            ys[i] = tuple(1 if m & bit else 0 for _, m in self.rhs)
        return xs, ys

    def __repr__(self):
        def side(terms):
            return " + ".join(
                (f"{c} " if c != 1 else "") + f"S({subset_label(m, self.n)})"
                for c, m in terms
            )
        return f"{side(self.lhs)} >= {side(self.rhs)}"


def _dist(w, u, v):
    return sum(wk for wk, uk, vk in zip(w, u, v) if uk != vk)


def check_contraction(ineq: Inequality, f: dict) -> list[str]:
    """Return all violations of (C1)/(C2)/totality; [] means f is a proof."""
    errors = []
    domain = list(product((0, 1), repeat=ineq.L))
    for x in domain:
        if x not in f:
            errors.append(f"map not defined on {x}")
        elif len(f[x]) != ineq.R or any(b not in (0, 1) for b in f[x]):
            errors.append(f"bad image for {x}: {f[x]}")
    if errors:
        return errors
    xs, ys = ineq.occurrence_vectors()
    for i in range(ineq.n + 1):
        if f[xs[i]] != ys[i]:
            errors.append(f"(C1) boundary label {i}: f({xs[i]})={f[xs[i]]} != {ys[i]}")
    for a in range(len(domain)):
        for b in range(a + 1, len(domain)):
            x, xp = domain[a], domain[b]
            if _dist(ineq.beta, f[x], f[xp]) > _dist(ineq.alpha, x, xp):
                errors.append(f"(C2) pair {x},{xp}")
    return errors


def find_contraction_bruteforce(ineq: Inequality) -> dict | None:
    """Exhaustive search over maps; only sane for tiny L (free points <= ~5)."""
    xs, ys = ineq.occurrence_vectors()
    fixed = {}
    for i in range(ineq.n + 1):
        if fixed.get(xs[i], ys[i]) != ys[i]:
            return None  # inconsistent boundary conditions: no map can exist
        fixed[xs[i]] = ys[i]
    domain = list(product((0, 1), repeat=ineq.L))
    free = [x for x in domain if x not in fixed]
    images = list(product((0, 1), repeat=ineq.R))
    for choice in product(images, repeat=len(free)):
        f = dict(fixed)
        f.update(zip(free, choice))
        if not check_contraction(ineq, f):
            return f
    return None


def find_contraction_symmetric_expanded(
    ineq: Inequality, time_limit_s: float = 1500.0, workers: int = 6
):
    """Contraction map on the UNIT-EXPANDED cube, restricted to maps symmetric
    under permuting identical copies (the weighted-cube method can be
    genuinely infeasible — Q3 is — while the expanded cube still admits maps).

    Expansion: a term c*S(T) becomes c unit coordinates. A copy-symmetric map
    depends only on the per-group counts of ones, and its image is taken
    canonically (first k coordinates of each group set). Domain classes are
    count tuples K in prod[0..s_g]; the image is a count tuple c(K). Adjacent
    classes (one coordinate flip) must satisfy sum_h |c_h(K) - c_h(K')| <= 1,
    which by canonical lifting and the hypercube path metric makes the lifted
    map a genuine contraction. Symmetry is a search restriction, NOT proven
    complete: FEASIBLE => theorem; INFEASIBLE => only 'no symmetric map'.

    Returns {class_tuple: count_tuple} or None; solver status in
    find_contraction_symmetric_expanded.last_status.
    """
    from itertools import product as iproduct

    from ortools.sat.python import cp_model

    Lg = [(m, c) for c, m in ineq.lhs]   # (mask, multiplicity)
    Rg = [(m, c) for c, m in ineq.rhs]
    sL = [c for _, c in Lg]
    sR = [c for _, c in Rg]

    classes = list(iproduct(*(range(s + 1) for s in sL)))
    anchors = []
    for i in range(ineq.n + 1):
        bit = 0 if i == ineq.n else (1 << i)
        xK = tuple(s if m & bit else 0 for (m, _), s in zip(Lg, sL))
        yK = tuple(s if m & bit else 0 for (m, _), s in zip(Rg, sR))
        anchors.append((xK, yK))

    # Domain tightening (pure preprocessing): the lifted map must satisfy
    # |c_h(K) - y_h(anchor)| <= d1(K, anchor) for every boundary anchor,
    # since anchors have fixed images and d1 on counts is the canonical-rep
    # cube distance. Near anchors this pins most variables outright.
    model = cp_model.CpModel()
    C = {}
    for K in classes:
        row = []
        for h in range(len(Rg)):
            lo, hi = 0, sR[h]
            for xK, yK in anchors:
                d = sum(abs(a - b) for a, b in zip(K, xK))
                lo = max(lo, yK[h] - d)
                hi = min(hi, yK[h] + d)
            if lo > hi:
                find_contraction_symmetric_expanded.last_status = "INFEASIBLE"
                return None  # no symmetric map can satisfy the anchor bounds
            row.append(model.NewIntVar(lo, hi, f"c_{K}_{h}"))
        C[K] = row

    # adjacency: images of one-flip-apart classes differ by at most one unit
    for K in classes:
        for g in range(len(sL)):
            if K[g] < sL[g]:
                K2 = K[:g] + (K[g] + 1,) + K[g + 1:]
                bools = []
                for h in range(len(Rg)):
                    b = model.NewBoolVar(f"d_{K}_{g}_{h}")
                    model.Add(C[K][h] - C[K2][h] <= b)
                    model.Add(C[K2][h] - C[K][h] <= b)
                    bools.append(b)
                model.Add(sum(bools) <= 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_search_workers = workers
    status = solver.Solve(model)
    find_contraction_symmetric_expanded.last_status = solver.StatusName(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    cmap = {K: tuple(solver.Value(C[K][h]) for h in range(len(Rg))) for K in classes}
    errs = check_symmetric_expanded(ineq, cmap)
    assert not errs, f"solver map failed verification: {errs[:3]}"
    return cmap


def check_symmetric_expanded(ineq: Inequality, cmap: dict) -> list[str]:
    """Independent verification of a symmetric expanded-cube map: totality,
    image bounds, boundary anchors, and the adjacency contraction condition
    (sufficient for all pairs by the path metric of the unit hypercube)."""
    from itertools import product as iproduct

    Lg = [(m, c) for c, m in ineq.lhs]
    Rg = [(m, c) for c, m in ineq.rhs]
    sL = [c for _, c in Lg]
    sR = [c for _, c in Rg]
    errors = []
    classes = list(iproduct(*(range(s + 1) for s in sL)))
    for K in classes:
        v = cmap.get(K)
        if v is None or len(v) != len(sR) or any(
            not (0 <= x <= s) for x, s in zip(v, sR)
        ):
            errors.append(f"bad image for class {K}")
            return errors
    for i in range(ineq.n + 1):
        bit = 0 if i == ineq.n else (1 << i)
        xK = tuple(s if m & bit else 0 for (m, _), s in zip(Lg, sL))
        yK = tuple(s if m & bit else 0 for (m, _), s in zip(Rg, sR))
        if cmap[xK] != yK:
            errors.append(f"boundary label {i}: f({xK}) = {cmap[xK]} != {yK}")
    for K in classes:
        for g in range(len(sL)):
            if K[g] < sL[g]:
                K2 = K[:g] + (K[g] + 1,) + K[g + 1:]
                if sum(abs(a - b) for a, b in zip(cmap[K], cmap[K2])) > 1:
                    errors.append(f"adjacency {K} -> {K2}")
    return errors


def find_contraction_cpsat(ineq: Inequality, time_limit_s: float = 120.0,
                           workers: int = 6) -> dict | None:
    """CP-SAT search. Constrains (C2) on hypercube edges only (sufficient by
    the path-metric argument); the returned map is re-verified on all pairs
    by check_contraction before being trusted."""
    from ortools.sat.python import cp_model

    xs, ys = ineq.occurrence_vectors()
    fixed = {}
    for i in range(ineq.n + 1):
        if fixed.get(xs[i], ys[i]) != ys[i]:
            return None
        fixed[xs[i]] = ys[i]

    domain = list(product((0, 1), repeat=ineq.L))
    model = cp_model.CpModel()
    F = {x: [model.NewBoolVar(f"f_{x}_{r}") for r in range(ineq.R)] for x in domain}
    for x, y in fixed.items():
        for r in range(ineq.R):
            model.Add(F[x][r] == y[r])
    beta_total = sum(ineq.beta)
    for x in domain:
        for l in range(ineq.L):
            if not x[l]:  # each hypercube edge once: flip a 0 to 1
                xp = x[:l] + (1,) + x[l + 1:]
                d = ineq.alpha[l]
                if d >= beta_total:
                    continue  # vacuous
                diffs = []
                for r in range(ineq.R):
                    dr = model.NewBoolVar(f"d_{x}_{l}_{r}")
                    model.Add(dr >= F[x][r] - F[xp][r])
                    model.Add(dr >= F[xp][r] - F[x][r])
                    diffs.append(dr)
                model.Add(
                    sum(b * dr for b, dr in zip(ineq.beta, diffs)) <= d
                )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_search_workers = workers
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # INFEASIBLE here is a theorem: the edge encoding admits every valid
        # map, so no contraction map exists on the *weighted* cube. (The
        # unit-expanded cube — repeat each term coeff times — may still admit
        # one; that needs the 2403.13283 machinery.)
        find_contraction_cpsat.last_status = solver.StatusName(status)
        return None
    find_contraction_cpsat.last_status = solver.StatusName(status)
    f = {x: tuple(int(solver.Value(F[x][r])) for r in range(ineq.R)) for x in domain}
    assert not check_contraction(ineq, f), "CP-SAT map failed full verification"
    return f

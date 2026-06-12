"""LP cut-assignment realizer — the principled T1/T2 engine (SPEC.md §6).

For a FIXED topology, S(I) is the min over bulk-side assignments (cuts) of a
linear function of edge weights. Realizing a target r therefore splits into
a combinatorial outer problem (which cut achieves each S(I)) and an LP inner
problem on the weights. This module solves the inner problem by iterated
re-pinning with lazy cut generation:

  1. start from random integer weights on the sampled topology;
  2. compute all entropies and their achieving-cut crossing patterns;
  3. pin each subset's current achieving pattern as an equality (with
     slacks), keep every pattern ever seen as a lower-bound constraint
     (each is *some* cut, so  pattern . w >= r_I  must hold), and solve the
     LP minimizing total slack;
  4. install the rationalized solution as new weights and repeat until the
     slack hits zero and the exact recomputation matches.

Claims discipline: the loop runs on floats/rationals for speed, but a hit is
only returned after scaling to integer weights (LCM of denominators) and
recomputing the full entropy vector in the exact reference path. Misses mean
nothing (the outer search is sampled, not exhaustive).

Sampled super-topologies include complete graphs on boundary + k bulk: the
LP can zero out edges, so it discovers sparse structure on its own.
"""

from __future__ import annotations

import random
from fractions import Fraction
from math import lcm

import networkx as nx
import numpy as np
from scipy.optimize import linprog

from hec.entropy import PURIFIER, boundary_vertices, entropy_vector
from hec.graphs import random_tree
from hec.subsets import vector_from_paper

_SRC, _SNK = "_s", "_t"


def _entropies_and_patterns(G, n, edges):
    """All S(I) plus the achieving cut's edge-crossing pattern, exactly."""
    H = G.copy()
    H.add_node(_SRC)
    H.add_node(_SNK)
    boundary = boundary_vertices(n)
    S, pat = {}, {}
    for mask in range(1, 1 << n):
        inside = [i for i in range(n) if mask >> i & 1]
        outside = [v for v in boundary if not (isinstance(v, int) and mask >> v & 1)]
        H.add_edges_from((_SRC, v) for v in inside)
        H.add_edges_from((_SNK, v) for v in outside)
        value, (reach, _) = nx.minimum_cut(H, _SRC, _SNK, capacity="capacity")
        side = {v: v in reach for v in G.nodes}
        S[mask] = value
        pat[mask] = tuple(1 if side[u] != side[v] else 0 for u, v in edges)
        H.remove_edges_from(list(H.edges(_SRC)))
        H.remove_edges_from(list(H.edges(_SNK)))
    return S, pat


def _certify(G, n, target):
    """Integerize weights and verify exactly. Returns (G_int, scale) or None."""
    caps = [d["capacity"] for _, _, d in G.edges(data=True)]
    caps = [c if isinstance(c, Fraction) else Fraction(c) for c in caps]
    L = lcm(*(c.denominator for c in caps)) if caps else 1
    Gi = nx.Graph()
    Gi.add_nodes_from(G.nodes)
    for u, v, d in G.edges(data=True):
        w = Fraction(d["capacity"]) * L
        assert w.denominator == 1
        if w:
            Gi.add_edge(u, v, capacity=int(w))
    want = {m: L * r for m, r in target.items()}
    if entropy_vector(Gi, n) == want:
        return Gi, L
    return None


def _set_weights(G, edges, x):
    for (u, v), val in zip(edges, x):
        G[u][v]["capacity"] = Fraction(float(val)).limit_denominator(10**6)


def _slack_lp(masks, pins, seen, target, m):
    """min total slack st  pins.w - r = s+ - s-,  every seen cut >= r,  w >= 0.
    Returns (weights, slack) or (None, inf)."""
    nm = len(masks)
    c = np.concatenate([np.zeros(m), np.ones(2 * nm)])
    A_eq = np.zeros((nm, m + 2 * nm))
    b_eq = np.zeros(nm)
    for i, k in enumerate(masks):
        A_eq[i, :m] = pins[k]
        A_eq[i, m + i] = -1.0
        A_eq[i, m + nm + i] = 1.0
        b_eq[i] = target[k]
    rows_ub, b_ub = [], []
    for k in masks:
        for p in seen[k]:
            row = np.zeros(m + 2 * nm)
            row[:m] = [-x for x in p]
            rows_ub.append(row)
            b_ub.append(-target[k])
    res = linprog(
        c,
        A_ub=np.array(rows_ub) if rows_ub else None,
        b_ub=np.array(b_ub) if b_ub else None,
        A_eq=A_eq, b_eq=b_eq,
        bounds=[(0, None)] * (m + 2 * nm),
        method="highs",
    )
    if not res.success:
        return None, float("inf")
    return res.x[:m], float(np.sum(res.x[m:]))


def _hard_lp(masks, pins, seen, target, m):
    """min sum w st  pins.w = r,  every other seen cut >= r,  w >= 0."""
    A_eq = np.array([pins[k] for k in masks], dtype=float)
    b_eq = np.array([target[k] for k in masks], dtype=float)
    rows_ub, b_ub = [], []
    for k in masks:
        for p in seen[k]:
            if p != pins[k]:
                rows_ub.append([-x for x in p])
                b_ub.append(-target[k])
    res = linprog(
        np.ones(m),
        A_ub=np.array(rows_ub) if rows_ub else None,
        b_ub=np.array(b_ub) if b_ub else None,
        A_eq=A_eq, b_eq=b_eq,
        bounds=[(0, None)] * m,
        method="highs",
    )
    return res.x if res.success else None


def fit_weights(G0, n, target, rng, descents=40, cut_rounds=40, patience=8,
                warm=False):
    """Two-phase solve on a fixed topology. Returns (G_int, scale) or None.

    Phase 1 descends with the slack LP: pin each subset's current achieving
    pattern softly, minimize total deviation, install the solution, re-pin.
    When the slack reaches zero, phase 2 runs constraint generation with the
    pins as hard equalities — a complete decision procedure for that pin
    assignment (each entropy is then <= target, so either everything matches
    exactly or a violated cut joins the pool). Hard infeasibility returns to
    the descent with the enlarged cut pool.
    """
    G = G0.copy()
    edges = list(G.edges())
    m = len(edges)
    rmax = max(target.values())
    if not warm:
        for u, v in edges:
            G[u][v]["capacity"] = Fraction(rng.randint(1, rmax))

    masks = sorted(target)
    seen: dict[int, set] = {k: set() for k in masks}
    best_slack, stall = float("inf"), 0

    for _ in range(descents):
        S, pat = _entropies_and_patterns(G, n, edges)
        if all(S[k] == target[k] for k in masks):
            hit = _certify(G, n, target)
            if hit:
                return hit
        for k in masks:
            seen[k].add(pat[k])

        w, slack = _slack_lp(masks, pat, seen, target, m)
        if w is None:
            return None
        _set_weights(G, edges, w)

        if slack < 1e-7:
            # phase 2: decide this pin assignment exactly
            pins = dict(pat)
            for _ in range(cut_rounds):
                x = _hard_lp(masks, pins, seen, target, m)
                if x is None:
                    break  # assignment impossible; back to descent
                _set_weights(G, edges, x)
                S2, pat2 = _entropies_and_patterns(G, n, edges)
                if all(S2[k] == target[k] for k in masks):
                    hit = _certify(G, n, target)
                    if hit:
                        return hit
                low = [k for k in masks if S2[k] < target[k]]
                if not low:
                    break  # rationalization drift; re-enter descent
                for k in low:
                    seen[k].add(pat2[k])
            stall = 0  # pool grew; descent restarts meaningfully
        elif slack >= best_slack - 1e-9:
            stall += 1
            if stall > patience:
                # shake: re-randomize a few weights to escape the basin
                for _ in range(max(1, m // 6)):
                    u, v = edges[rng.randrange(m)]
                    G[u][v]["capacity"] = Fraction(rng.randint(1, rmax))
                stall = 0
        best_slack = min(best_slack, slack)
    return None


def _complete_topology(n, b):
    G = nx.complete_graph(boundary_vertices(n) + [f"b{i}" for i in range(b)])
    for u, v in G.edges():
        G[u][v]["capacity"] = 1
    return G


def _hub_topology(n, rng, hubs):
    G = nx.Graph()
    hub_names = [f"b{i}" for i in range(hubs)]
    for i in range(hubs - 1):
        G.add_edge(hub_names[i], hub_names[i + 1], capacity=1)
    for v in boundary_vertices(n):
        G.add_edge(rng.choice(hub_names), v, capacity=1)
    return G


def sample_topology(n, rng):
    roll = rng.random()
    if roll < 0.40:
        return _complete_topology(n, rng.randint(1, 6))
    if roll < 0.60:
        return _hub_topology(n, rng, rng.randint(1, 3))
    G = random_tree(n, rng, n_bulk=rng.randint(0, 5), wmax=4)
    if roll < 0.80:
        verts = list(G.nodes)
        for _ in range(rng.randint(1, 3)):
            u, v = rng.sample(verts, 2)
            if not G.has_edge(u, v):
                G.add_edge(u, v, capacity=1)
    return G


def lp_realize_target(target, n, rng, attempts=60, descents=40):
    """Outer search. target: paper-order tuple or {mask: int}. Returns
    (G_int, scale) with entropy_vector(G_int, n) == scale * target, or None.

    Every third attempt warm-starts the LP from a short v1 hill-climb on the
    same topology — the climb gets the pin assignment mostly right, the LP
    finishes the job with rational weights.
    """
    from hec.realize import _score  # cheap integer L1 objective for the climb

    tgt = target if isinstance(target, dict) else vector_from_paper(target, n)
    deterministic = [_complete_topology(n, b) for b in (1, 2, 3, 4, 5)]
    for a in range(attempts):
        G0 = deterministic[a] if a < len(deterministic) else sample_topology(n, rng)
        warm = a >= len(deterministic) and a % 3 == 0
        if warm:
            rmax = max(tgt.values())
            for u, v in G0.edges():
                G0[u][v]["capacity"] = rng.randint(1, rmax)
            edges = list(G0.edges())
            best = _score(G0, n, tgt)
            for _ in range(1200):
                if best == 0:
                    break
                u, v = edges[rng.randrange(len(edges))]
                old = G0[u][v]["capacity"]
                new = old + rng.choice((-2, -1, 1, 2))
                if new < 0:
                    continue
                G0[u][v]["capacity"] = new
                s = _score(G0, n, tgt)
                if s <= best:
                    best = s
                else:
                    G0[u][v]["capacity"] = old
        hit = fit_weights(G0, n, tgt, rng, descents=descents, warm=warm)
        if hit:
            return hit
    return None

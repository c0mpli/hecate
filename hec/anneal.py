"""Topology annealing: local search over sparse graph structures, with the
LP weight-fitter's best-achieved slack as the fitness signal.

Oracle-mode finding (NOTES.md session 4): fit_weights recovers weights in
seconds ON the right topology, and random sampling essentially never draws
that topology. The missing capability is structure search. Moves are small
edits in the sparse-bulk family (re-home/add/delete a boundary strap, toggle
a bulk-bulk edge, add/remove a bulk vertex); fitness of a topology is the
smallest slack a short fit_weights probe reaches on it. Slack decreases
roughly monotonically as the structure approaches a realizing one, which is
exactly what simulated annealing wants.

Any hit returned here was certified inside fit_weights (integer weights,
exact entropy_vector match) — the annealer only decides where to look.
"""

from __future__ import annotations

import math
import random

import networkx as nx

from hec.entropy import boundary_vertices
from hec.lp_realize import _sparse_bulk_topology, fit_weights
from hec.subsets import vector_from_paper


def _bulks(G):
    return [v for v in G.nodes if isinstance(v, str) and v.startswith("b")]


def _connected_ok(G, n):
    return nx.is_connected(G) and all(G.degree(v) >= 1 for v in boundary_vertices(n))


def mutate(G, n, rng, max_bulk=7, max_bdeg=3):
    """One random structural edit; returns a valid neighbor or None."""
    for _ in range(20):  # retry until a move applies
        H = G.copy()
        bulks = _bulks(H)
        move = rng.randrange(6)
        if move == 0:  # re-home one boundary strap
            v = rng.choice(boundary_vertices(n))
            nbrs = [u for u in H[v]]
            if not nbrs or len(bulks) < 2:
                continue
            old = rng.choice(nbrs)
            new = rng.choice([b for b in bulks if b != old])
            if H.has_edge(v, new):
                continue
            H.remove_edge(v, old)
            H.add_edge(v, new, capacity=1)
        elif move == 1:  # add a strap
            v = rng.choice(boundary_vertices(n))
            cands = [b for b in bulks if not H.has_edge(v, b)]
            if H.degree(v) >= max_bdeg or not cands:
                continue
            H.add_edge(v, rng.choice(cands), capacity=1)
        elif move == 2:  # delete a strap
            v = rng.choice(boundary_vertices(n))
            if H.degree(v) <= 1:
                continue
            H.remove_edge(v, rng.choice(list(H[v])))
        elif move == 3:  # toggle a bulk-bulk edge
            if len(bulks) < 2:
                continue
            u, w = rng.sample(bulks, 2)
            if H.has_edge(u, w):
                H.remove_edge(u, w)
            else:
                H.add_edge(u, w, capacity=1)
        elif move == 4:  # add a bulk vertex attached to two random nodes
            if len(bulks) >= max_bulk:
                continue
            new = f"b{max(int(b[1:]) for b in bulks) + 1 if bulks else 0}"
            a, c = rng.sample(list(H.nodes), 2)
            H.add_edge(new, a, capacity=1)
            H.add_edge(new, c, capacity=1)
        else:  # remove a low-degree bulk vertex
            cands = [b for b in bulks if H.degree(b) <= 2]
            if len(bulks) <= 1 or not cands:
                continue
            H.remove_node(rng.choice(cands))
        if _connected_ok(H, n):
            return H
    return None


def anneal_topology(target, n, rng, iters=350, probe_descents=12, t0=1.5,
                    log=None):
    """Returns (G_int, scale) certified, or None. target: tuple or dict."""
    tgt = target if isinstance(target, dict) else vector_from_paper(target, n)
    G = _sparse_bulk_topology(n, rng)
    hit, slack = fit_weights(G, n, tgt, rng, descents=probe_descents, report=True)
    if hit:
        return hit
    best_G, best_s = G, slack
    for it in range(iters):
        T = t0 * (1.0 - it / iters) + 1e-3
        H = mutate(best_G if rng.random() < 0.7 else G, n, rng)
        if H is None:
            continue
        hit, s = fit_weights(H, n, tgt, rng, descents=probe_descents, report=True)
        if hit:
            return hit
        if s < slack or rng.random() < math.exp(-(s - slack) / max(T, 1e-6)):
            G, slack = H, s
        if s < best_s:
            best_G, best_s = H, s
            if log:
                log(f"iter {it}: slack {s:.3f}")
        # occasional restart from the best-so-far basin
        if it % 60 == 59:
            G, slack = best_G, best_s
    return None

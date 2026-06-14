"""Non-simple tree search: party-splitting topology annealing.

A NON-SIMPLE tree graph model lets a party label several boundary vertices
(leaves), with overall tree topology (no cycles at all). This is the class
that can realize entropy vectors which admit no SIMPLE tree (the chordality-
failing ones) yet are still tree-realizable — the open question for the two
bulk-cycle orbits of arXiv:2412.15364 (s=111, s=207) and the strong tree
conjecture of arXiv:2204.00075.

Design: the LP cut-assignment fitter is pattern-agnostic, so we reuse its
slack/hard LPs from hec.lp_realize and only supply (i) labeled min-cut
patterns (a party's cut separates ALL its leaf copies) and (ii) labeled
exact certification. The annealer walks tree space with party-splitting and
regraft moves, scored by the fitter's best slack.

Every returned model is exact-certified (integer weights, entropy_vector_
labeled == scale * target). Annealer FAILURE is never evidence of anything
(user policy): non-realizability is Track B's job, not this module's.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from math import lcm

import networkx as nx

from hec.entropy import entropy_vector_labeled
from hec.lp_realize import _hard_lp, _set_weights, _slack_lp
from hec.subsets import vector_from_paper

_SRC, _SNK = "_src", "_snk"


def party_leaves(party: dict, n: int):
    return party


def _patterns_labeled(G, n, party, edges):
    """(S, pattern) per subset, with party-group source/sink. pattern[k] is a
    0/1 tuple over `edges`: which tree edges the minimal min-cut crosses."""
    H = nx.Graph()
    H.add_nodes_from(G.nodes)
    for u, v, d in G.edges(data=True):
        if u != v:
            H.add_edge(u, v, capacity=d["capacity"])
    H.add_node(_SRC)
    H.add_node(_SNK)
    S, pat = {}, {}
    for mask in range(1, 1 << n):
        inside = [v for v, p in party.items() if isinstance(p, int) and mask >> p & 1]
        outside = [v for v, p in party.items()
                   if not (isinstance(p, int) and mask >> p & 1)]
        H.add_edges_from((_SRC, v) for v in inside)
        H.add_edges_from((_SNK, v) for v in outside)
        value, (reach, _) = nx.minimum_cut(H, _SRC, _SNK, capacity="capacity")
        side = {v: v in reach for v in G.nodes}
        S[mask] = value
        pat[mask] = tuple(1 if side[u] != side[v] else 0 for u, v in edges)
        H.remove_edges_from(list(H.edges(_SRC)))
        H.remove_edges_from(list(H.edges(_SNK)))
    return S, pat


def _certify_labeled(G, n, party, target):
    caps = [Fraction(d["capacity"]) for _, _, d in G.edges(data=True)]
    L = lcm(*(c.denominator for c in caps)) if caps else 1
    Gi = nx.Graph()
    Gi.add_nodes_from(G.nodes)
    for u, v, d in G.edges(data=True):
        w = Fraction(d["capacity"]) * L
        assert w.denominator == 1
        if w:
            Gi.add_edge(u, v, capacity=int(w))
    want = {m: L * r for m, r in target.items()}
    if entropy_vector_labeled(Gi, n, party) == want:
        return Gi, L
    return None


def fit_tree_weights(G0, party, n, target, rng, descents=30, cut_rounds=30,
                     patience=6, report=False):
    """LP weight fit on a fixed labeled tree. Returns (G_int, scale) or None."""
    G = G0.copy()
    edges = list(G.edges())
    m = len(edges)
    rmax = max(target.values())
    for u, v in edges:
        G[u][v]["capacity"] = Fraction(rng.randint(1, rmax))
    masks = sorted(target)
    seen = {k: set() for k in masks}
    best_slack = float("inf")
    stall = 0
    for _ in range(descents):
        S, pat = _patterns_labeled(G, n, party, edges)
        if all(S[k] == target[k] for k in masks):
            hit = _certify_labeled(G, n, party, target)
            if hit:
                return (hit, 0.0) if report else hit
        for k in masks:
            seen[k].add(pat[k])
        w, slack = _slack_lp(masks, pat, seen, target, m)
        if w is None:
            return (None, best_slack) if report else None
        _set_weights(G, edges, w)
        if slack < 1e-7:
            pins = dict(pat)
            for _ in range(cut_rounds):
                x = _hard_lp(masks, pins, seen, target, m)
                if x is None:
                    break
                _set_weights(G, edges, x)
                S2, pat2 = _patterns_labeled(G, n, party, edges)
                if all(S2[k] == target[k] for k in masks):
                    hit = _certify_labeled(G, n, party, target)
                    if hit:
                        return (hit, 0.0) if report else hit
                low = [k for k in masks if S2[k] < target[k]]
                if not low:
                    break
                for k in low:
                    seen[k].add(pat2[k])
            stall = 0
        elif slack >= best_slack - 1e-9:
            stall += 1
            if stall > patience:
                for _ in range(max(1, m // 4)):
                    u, v = edges[rng.randrange(m)]
                    G[u][v]["capacity"] = Fraction(rng.randint(1, rmax))
                stall = 0
        best_slack = min(best_slack, slack)
    return (None, best_slack) if report else None


# ---- tree topology generation + mutation (party-labeled leaves) ----

def _labels(n):
    return list(range(n)) + ["O"]


def seed_tree(n, rng, extra_bulk=2):
    """A random labeled tree: one leaf per party/purifier on a small bulk
    backbone."""
    G = nx.Graph()
    hubs = [f"b{i}" for i in range(1 + extra_bulk)]
    for i in range(1, len(hubs)):
        G.add_edge(hubs[i], hubs[rng.randrange(i)], capacity=1)
    party = {}
    for j, lab in enumerate(_labels(n)):
        leaf = f"L{j}"
        G.add_edge(leaf, rng.choice(hubs), capacity=1)
        party[leaf] = lab
    return G, party


def mutate_tree(G, party, n, rng, max_leaves_per_party=4, max_bulk=14):
    """One tree-preserving edit; returns (G', party') or None."""
    for _ in range(24):
        H = G.copy()
        p = dict(party)
        bulks = [v for v in H if isinstance(v, str) and v.startswith("b")]
        leaves = [v for v in p]
        move = rng.randrange(6)
        nxt = (max(int(b[1:]) for b in bulks) + 1) if bulks else 0
        if move == 0 and len(bulks) < max_bulk:  # add a bulk vertex on an edge
            e = rng.choice(list(H.edges()))
            H.remove_edge(*e)
            b = f"b{nxt}"
            H.add_edge(e[0], b, capacity=1)
            H.add_edge(b, e[1], capacity=1)
        elif move == 1:  # split a party: add another leaf copy
            counts = {}
            for lab in p.values():
                counts[lab] = counts.get(lab, 0) + 1
            lab = rng.choice(_labels(n))
            if counts.get(lab, 0) >= max_leaves_per_party:
                continue
            leaf = f"S{nxt}{rng.randrange(10000)}"
            anchor = rng.choice(bulks + leaves) if bulks else rng.choice(leaves)
            H.add_edge(leaf, anchor, capacity=1)
            p[leaf] = lab
        elif move == 2:  # merge: drop a redundant party copy
            counts = {}
            for lab in p.values():
                counts[lab] = counts.get(lab, 0) + 1
            cand = [v for v in leaves if counts[p[v]] > 1 and H.degree(v) == 1]
            if not cand:
                continue
            v = rng.choice(cand)
            H.remove_node(v)
            del p[v]
        elif move == 3:  # regraft a leaf elsewhere
            v = rng.choice(leaves)
            if H.degree(v) != 1:
                continue
            old = next(iter(H[v]))
            targets = [u for u in list(bulks) + leaves if u != v and u != old]
            if not targets:
                continue
            H.remove_edge(v, old)
            H.add_edge(v, rng.choice(targets), capacity=1)
        elif move == 4:  # prune a degree-1 bulk vertex
            deg1 = [b for b in bulks if H.degree(b) == 1]
            if len(bulks) <= 1 or not deg1:
                continue
            H.remove_node(rng.choice(deg1))
        else:  # smooth out a degree-2 bulk vertex (contract)
            deg2 = [b for b in bulks if H.degree(b) == 2]
            if not deg2:
                continue
            b = rng.choice(deg2)
            a, c = list(H[b])
            H.remove_node(b)
            if not H.has_edge(a, c):
                H.add_edge(a, c, capacity=1)
        # validity: tree, connected, every party+purifier present
        if not nx.is_tree(H):
            continue
        if set(p.values()) != set(_labels(n)):
            continue
        return H, p
    return None


def _anneal_once(tgt, n, rng, iters, probe_descents, t0, seed_graph, log):
    if seed_graph is not None:
        G, party = seed_graph[0].copy(), dict(seed_graph[1])
    else:
        G, party = seed_tree(n, rng, extra_bulk=rng.randint(1, 4))
        # bias the seed toward the non-simple regime with a couple of splits
        for _ in range(rng.randint(0, 3)):
            mut = mutate_tree(G, party, n, rng)
            if mut:
                G, party = mut
    hit, slack = fit_tree_weights(G, party, n, tgt, rng,
                                  descents=probe_descents, report=True)
    if hit:
        return hit[0], hit[1], party
    best = cur = (G, party, slack)
    for it in range(iters):
        T = t0 * (1.0 - it / iters) + 1e-3
        base = best if rng.random() < 0.7 else cur
        mut = mutate_tree(base[0], base[1], n, rng)
        if mut is None:
            continue
        H, p = mut
        hit, s = fit_tree_weights(H, p, n, tgt, rng,
                                  descents=probe_descents, report=True)
        if hit:
            return hit[0], hit[1], p
        if s < cur[2] or rng.random() < math.exp(-(s - cur[2]) / max(T, 1e-6)):
            cur = (H, p, s)
        if s < best[2]:
            best = (H, p, s)
            if log:
                log(f"iter {it}: slack {s:.3f}, {len(p)} leaves, "
                    f"{sum(1 for v in H if isinstance(v,str) and v.startswith('b'))} bulk")
        if it % 70 == 69:
            cur = best
    return None


def anneal_tree(target, n, rng, iters=400, probe_descents=10, t0=1.5,
                restarts=1, seed_graph=None, log=None):
    """Search for a non-simple TREE realizing `target`. Returns (G_int, scale,
    party) certified, or None.

    seed_graph: optional (G, party) to start from — e.g. the boundary-split of
    a known cyclic realization, the real 111/207 workflow (split, then let the
    annealer break the surviving bulk cycle)."""
    tgt = target if isinstance(target, dict) else vector_from_paper(target, n)
    for r in range(restarts):
        res = _anneal_once(tgt, n, rng, iters, probe_descents, t0,
                           seed_graph if r == 0 else None, log)
        if res:
            return res
    return None

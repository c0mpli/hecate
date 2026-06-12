#!/usr/bin/env python3
"""Verify the transcribed published graphs (P2 closing item), then use them
as oracles for the LP realizer.

Stage 1 (--verify, default): each transcribed graph must yield exactly
scale * ray_k for its k (scales 1..4 tried). Failures get a single-edit
variant search (flip a weight 1<->2<->3, or re-home one edge endpoint among
bulk vertices) against the same exact oracle — useful because a couple of
figure labels are visually ambiguous; the entropy vector is not.

Stage 2 (--oracle): for the rays the cold LP search hasn't realized, run
fit_weights on the PUBLISHED topology (weights stripped). Recovers weights
=> the gap is topology generation; fails => the weight-fitting formulation
is the problem. This is the diagnostic the mystery campaign needs.
"""

import argparse
import itertools
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.entropy import entropy_vector
from hec.subsets import vector_from_paper

HOLDOUTS = [10, 12, 16, 17, 18, 19]


def build(edges):
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 4, "O"])
    for u, v, w in edges:
        G.add_edge(u, v, capacity=w)
    return G


def matches(edges, k):
    """Return scale if graph == scale * ray_k exactly, else None."""
    tgt = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
    S = entropy_vector(build(edges), 5)
    for s in (1, 2, 3, 4):
        if all(S[m] == s * tgt[m] for m in tgt):
            return s
    return None


PERMS = list(itertools.permutations(range(6)))  # labels 0..4, 5 = O


def orbit_match(edges, k):
    """One exact S-vector, then scan Sym(6) as index permutations of the
    vector (microseconds each). Returns (scale, perm) or None; perm maps
    current label -> correct label (5 = O)."""
    from hec.cone import permute_vector

    tgt = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
    S = entropy_vector(build(edges), 5)
    for perm in PERMS:
        Sp = permute_vector(S, perm, 5)
        for s in (1, 2, 3, 4):
            if all(Sp[m] == s * tgt[m] for m in tgt):
                return s, perm
    return None


def apply_perm(edges, perm):
    """Relabel boundary vertices of an edge list by perm (5 = O)."""
    lab = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, "O": 5}
    inv = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: "O"}

    def m(x):
        if isinstance(x, str) and x.startswith("b"):
            return x
        return inv[perm[lab[x]]]

    return [(m(u), m(v), w) for u, v, w in edges]


def variants(edges):
    """Single-edit neighbors of a transcription: weight flips and endpoint
    re-homing among bulk vertices (figure-ambiguity moves)."""
    bulks = sorted({x for e in edges for x in e[:2]
                    if isinstance(x, str) and x.startswith("b")})
    for i, (u, v, w) in enumerate(edges):
        for w2 in (1, 2, 3):
            if w2 != w:
                yield edges[:i] + [(u, v, w2)] + edges[i + 1:]
        for side, other in ((u, v), (v, u)):
            if isinstance(side, str) and side.startswith("b"):
                for b2 in bulks:
                    if b2 != side and (other, b2) != (u, v):
                        yield edges[:i] + [(other, b2, w)] + edges[i + 1:]


def stage_verify():
    bad = []
    for k in range(1, 20):
        edges = [tuple(e) for e in C5_PUBLISHED_GRAPHS[k]]
        s = matches(edges, k)
        if s:
            print(f"graph {k:2d}: OK (scale {s}, {len(edges)} edges)")
            continue
        fixed = None
        how = ""
        om = orbit_match(edges, k)
        if om:
            sc, perm = om
            fixed, how = (apply_perm(edges, perm), sc), f"relabel {perm}"
        if not fixed:
            for cand in variants(edges):
                om = orbit_match(cand, k)
                if om:
                    sc, perm = om
                    fixed, how = (apply_perm(cand, perm), sc), f"edit+relabel {perm}"
                    break
        if not fixed:
            # two weight edits + relabel (weights are the most misread)
            m = len(edges)
            done = False
            for i in range(m):
                for wi in (1, 2, 3):
                    if wi == edges[i][2]:
                        continue
                    e1 = edges[:i] + [edges[i][:2] + (wi,)] + edges[i + 1:]
                    for j in range(i + 1, m):
                        for wj in (1, 2, 3):
                            if wj == edges[j][2]:
                                continue
                            cand = e1[:j] + [e1[j][:2] + (wj,)] + e1[j + 1:]
                            om = orbit_match(cand, k)
                            if om:
                                sc, perm = om
                                fixed = (apply_perm(cand, perm), sc)
                                how = f"2 weight edits+relabel {perm}"
                                done = True
                                break
                        if done:
                            break
                    if done:
                        break
                if done:
                    break
        if fixed:
            cand, sc = fixed
            assert matches(cand, k) == sc
            print(f"graph {k:2d}: FIXED via {how} (scale {sc})")
            print(f"          corrected edges: {sorted(cand, key=str)}")
            bad.append((k, cand))
        else:
            print(f"graph {k:2d}: MISMATCH — needs figure re-read")
            bad.append((k, None))
    return bad


def stage_oracle(seed):
    from hec.lp_realize import fit_weights

    print("\n--- oracle mode: published topology, weights stripped ---")
    for k in HOLDOUTS:
        edges = C5_PUBLISHED_GRAPHS[k]
        G = build(edges)
        tgt = vector_from_paper(C5_EXTREME_RAYS[k - 1], 5)
        hit = None
        for attempt in range(8):
            rng = random.Random(seed + 100 * k + attempt)
            hit = fit_weights(G, 5, tgt, rng, descents=60)
            if hit:
                break
        if hit:
            Gi, s = hit
            print(f"ray {k:2d}: weights RECOVERED on published topology "
                  f"(scale {s}) -> generator gap, not formulation bug")
        else:
            print(f"ray {k:2d}: NOT recovered on published topology "
                  f"-> suspect fit_weights formulation/search")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--oracle", action="store_true")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    bad = stage_verify()
    if any(fix is None for _, fix in bad):
        sys.exit(1)
    if args.oracle:
        stage_oracle(args.seed)


if __name__ == "__main__":
    main()

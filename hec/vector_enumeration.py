"""hec/vector_enumeration.py — seed-independent decider for NON-SIMPLE tree
realizability, working from the entropy VECTOR.

Graph tools (search.py, cycle_surgery.py) start from ONE realization and apply
local moves; they bottom out on pure-bulk cycles and can't generate distinct
seeds. This tool never starts from a graph: it asks, from the vector v, whether
ANY refined party-structure (fine-graining) up to a bound N' admits a chordal
correlation hypergraph. By the Hubeny-Rota iff (arXiv:2512.24490) chordal => the
refined vector is simple-tree-realizable => coarse-graining back gives a
NON-SIMPLE tree for v.

SOUNDNESS NOTE (read this before trusting any output). The literal step the
source paper (arXiv:2512.18702) postpones is enumerating refined PMIs from v.
Rather than invert their hypergraph coarse-graining (unproven here, high risk of
a silent bug), we enumerate the refined HUB-STRUCTURES directly — non-simple
tree topologies whose leaves are colored by the original parties (a split) — and
exactly fit weights so the structure's coarse-graining equals v. Each hit is
then CERTIFIED through the validated pipeline of hec.fine_graining: its refined
simple tree is verified CHORDAL (the theorem's certificate) and coarse-grains
back to v exactly (the round-trip-validated `coarse_grain`). So:
  - every SUCCESS is exact and theorem-certified (chordal refined tree);
  - every NEGATIVE is BOUNDED by the enumerated structures (N', bulk, the
    leaf-boundary restriction) — NEVER "no tree exists", NEVER unbounded.
This is sound but INCOMPLETE: the enumeration is bounded, and it restricts
boundary vertices to tree leaves. A bounded negative is therefore evidence, not
proof, and its exact scope is recorded in every log.

HARD RULES enforced: only the bounded negative is permitted; exact arithmetic
certifies (the weight fit proposes in float, `certify_fine_graining` verifies in
exact arithmetic); candidates are pynauty-canonicalized so the distinct count is
meaningful; suspects {110,145,168} are never touched here.
"""

from __future__ import annotations

import itertools
import json
import pathlib
from fractions import Fraction

import networkx as nx

from hec.chordality import simple_forest_realizable
from hec.fine_graining import certify_fine_graining
from hec.subsets import vector_from_paper
from hec.tree_search import fit_tree_weights

REPORTS = pathlib.Path(__file__).resolve().parent.parent / "reports" / "realizations"


def _labels(n):
    return list(range(n)) + ["O"]


def split_structures(n, n_extra):
    """Canonical multiplicity vectors: how many EXTRA leaves each label (the n
    parties and the purifier) gets, summing to n_extra. A label with multiplicity
    m_i has 1+extra_i leaves. Returns list of dicts {label: total_copies}."""
    labels = _labels(n)
    out = []
    # distribute n_extra extra copies among len(labels) labels
    for combo in itertools.combinations_with_replacement(range(len(labels)), n_extra):
        mult = {l: 1 for l in labels}
        for idx in combo:
            mult[labels[idx]] += 1
        out.append(mult)
    # dedup identical dicts
    seen, uniq = set(), []
    for m in out:
        key = tuple(sorted((str(k), v) for k, v in m.items()))
        if key not in seen:
            seen.add(key)
            uniq.append(m)
    return uniq


def _canon_colored_tree(T, party):
    """pynauty key for a leaf-colored tree (color by original party label),
    so isomorphic colorings aren't recounted."""
    try:
        import pynauty
    except Exception:
        return (T.number_of_nodes(), tuple(sorted(str(party.get(v, "b")) for v in T)))
    nodes = list(T.nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    adj = {i: [idx[u] for u in T[v]] for i, v in enumerate(nodes)}
    groups = {}
    for v in nodes:
        groups.setdefault(str(party.get(v, "_bulk")), set()).add(idx[v])
    # CANONICAL color-class order (sorted by label) — pynauty's certificate
    # depends on the ORDER of the color classes, so an arbitrary (dict) order
    # makes the key non-isomorphism-invariant and the dedup UNSOUND (it drops
    # genuinely distinct structures). GATE 1 caught exactly this.
    coloring = [groups[k] for k in sorted(groups.keys()) if groups[k]]
    g = pynauty.Graph(len(nodes), directed=False, adjacency_dict=adj,
                      vertex_coloring=coloring)
    return pynauty.certificate(g)


def _multiset_perms(slots):
    """Distinct arrangements of a label multiset — avoids generating the
    duplicate-label permutations of itertools.permutations (the factorial-from-
    repeats). Sound: yields exactly the distinct sequences, no more, no fewer."""
    try:
        from sympy.utilities.iterables import multiset_permutations
        for p in multiset_permutations(slots):
            yield tuple(p)
    except Exception:
        seen = set()
        for p in itertools.permutations(slots):
            if p not in seen:
                seen.add(p)
                yield p


def colored_trees(n, mult, n_bulk, max_trees=10**9, _use_multiset=True):
    """Enumerate non-isomorphic trees whose LEAVES carry the colored boundary
    (each original label appears mult[label] times) and whose internal vertices
    are bulk. Yields (T, party), one per DISTINCT (pynauty-canonical) structure.
    Boundary == leaves (a stated restriction of this enumerator).

    OPTIMIZATION (sound — identical distinct set): distinct leaf-colorings are
    generated via multiset permutations (no duplicate-label perms) then deduped
    by pynauty canonical form. `_use_multiset=False` restores the naive
    all-permutations generation for the equivalence test."""
    n_boundary = sum(mult.values())
    n_nodes = n_boundary + n_bulk
    if n_nodes < 2 or n_boundary < 2:
        return
    boundary_slots = []
    for lab, m in mult.items():
        boundary_slots += [lab] * m
    # materialize as a reusable list — a generator would be exhausted after the
    # first tree, silently dropping colorings for the rest (an unsoundness the
    # equivalence test GATE A caught).
    perms = (list(_multiset_perms(boundary_slots)) if _use_multiset
             else list(set(itertools.permutations(boundary_slots))))
    seen = set()
    count = 0
    trees = [T0 for T0 in nx.nonisomorphic_trees(n_nodes)
             if sum(1 for v in T0.nodes if T0.degree(v) == 1) == n_boundary]
    for T0 in trees:
        leaves = [v for v in T0.nodes if T0.degree(v) == 1]
        internal = [v for v in T0.nodes if T0.degree(v) != 1]
        if len(internal) != n_bulk:
            continue
        base = nx.Graph()
        relabel = {}
        for i, v in enumerate(leaves):
            relabel[v] = ("L", i)
        for j, v in enumerate(internal):
            relabel[v] = f"b{j}"
        for a, b in T0.edges:
            base.add_edge(relabel[a], relabel[b], capacity=1)
        for perm in perms:
            party = {("L", i): perm[i] for i in range(len(leaves))}
            key = _canon_colored_tree(base, party)
            if key in seen:
                continue
            seen.add(key)
            yield base.copy(), party
            count += 1
            if count >= max_trees:
                return


def forced_positive_mi_reject(T, party, n, v_dict):
    """SOUND pre-LP rejection filter (necessary condition).

    SOUNDNESS PROOF (why this is necessary, and why cut-feasibility filters are
    WEAK for this problem — establish necessity BEFORE pruning, per protocol):

    A colored tree T realizes v iff SOME assignment of NON-NEGATIVE edge weights
    makes every labeled min-cut equal v. Crucially, weights may be ZERO, and a
    zero-weight edge is equivalent to deleting it. Therefore T realizes v iff
    some SUB-FOREST of T (delete any subset of edges) realizes v with strictly
    positive weights. Consequently, almost every cut-combinatorial "obstruction"
    on the full topology is CIRCUMVENTED by zeroing an interior edge — so cut-
    feasibility conditions are almost never necessary (you cannot reject a
    structure just because its FULL topology over-couples two groups; the LP may
    zero the coupling edge). This is the same lesson as chordality last session:
    the candidate condition is not necessary, so pruning on it is UNSOUND.

    The ONLY edges that CANNOT be zeroed are the leaf-edges of single-leaf
    parties (each party must keep a positive-weight leaf, else it vanishes from
    the boundary). The one robustly-necessary condition that survives: if two
    single-leaf parties a, b share a degree-2 bulk vertex (their leaves form an
    isolated pair a-b0-b with b0 connected to nothing else), then
    {a,b} is a separate component, so S(ab)=0 while S(a)=S(b)=min(w_a,w_b)>0
    (w_a,w_b forced positive), giving MI(a:b)=S(a)+S(b)-S(ab)>0 FORCED. So if v
    demands MI_v(a:b)=0, T cannot realize it -> REJECT. (Provably necessary.)

    This filter is SOUND but, as the proof and the 0%-combinatorial-hit-rate
    measurement show, it rejects almost nothing — the real discrimination is in
    the entropy VALUES (the LP), not the cut combinatorics. Reported honestly.
    """
    from hec.chordality import mutual_information

    # leaves per party label
    leaves = {}
    for vtx, lab in party.items():
        leaves.setdefault(lab, []).append(vtx)
    singles = {lab: ls[0] for lab, ls in leaves.items() if len(ls) == 1}
    for a in range(n):
        for b in range(a + 1, n):
            if a not in singles or b not in singles:
                continue
            if mutual_information(v_dict, 1 << a, 1 << b, n) != 0:
                continue  # v does not require MI(a:b)=0
            la, lb = singles[a], singles[b]
            na, nb = list(T[la]), list(T[lb])
            if na and na == nb and len(na) == 1:
                b0 = na[0]
                if b0 not in party and T.degree(b0) == 2:
                    return True  # isolated forced-positive-MI pair -> reject
    return False


def decide(name, v, n, bound, n_bulk_max=4, fit_attempts=4, fit_descents=40,
           out_dir=REPORTS, log=print, max_trees=4000, use_filter=False):
    """Decide non-simple tree realizability of v by bounded structure
    enumeration. Returns (cert | None, info). info records the bound, the count
    of DISTINCT structures tested, and (on negative) the exact bounded
    qualifier — never an unbounded non-existence claim."""
    import random

    Sd = v if isinstance(v, dict) else vector_from_paper(v, n)
    base = simple_forest_realizable(Sd, n)
    if base["chordal"]:
        from hec.tree_builder import build_simple_forest
        T = build_simple_forest(Sd, n)
        party = {x: x for x in T.nodes if not str(x).startswith("q")}
        cert = certify_fine_graining(T, party, Sd, n, name, out_dir, log)
        return cert, {"status": "tree", "n_prime": n, "route": "base_chordal",
                      "distinct_structures": 1}

    rng = random.Random(20260615)
    total_distinct = 0
    filtered = 0
    for n_extra in range(1, bound + 1):
        n_prime = n + n_extra
        for mult in split_structures(n, n_extra):
            for n_bulk in range(0, n_bulk_max + 1):
                for T, party in colored_trees(n, mult, n_bulk, max_trees=max_trees):
                    total_distinct += 1
                    if use_filter and forced_positive_mi_reject(T, party, n, Sd):
                        filtered += 1
                        continue  # provably cannot realize v (sound rejection)
                    hit = fit_tree_weights(T, party, n, Sd, rng,
                                           descents=fit_descents, report=False)
                    for _ in range(fit_attempts - 1):
                        if hit is not None:
                            break
                        hit = fit_tree_weights(T, party, n, Sd, rng,
                                               descents=fit_descents, report=False)
                    if hit is None:
                        continue
                    Gi, scale = hit
                    # rebuild integer-weighted tree with its party map for the cert
                    cert = certify_fine_graining(Gi, party, Sd, n, name, out_dir, log)
                    if cert is not None:
                        log(f"[{name}] tree found: N'={cert['n_prime']} "
                            f"(split {mult}, bulk {n_bulk}); {total_distinct} "
                            f"distinct structures tested")
                        return cert, {"status": "tree", "n_prime": cert["n_prime"],
                                      "distinct_structures": total_distinct,
                                      "route": "enumeration"}
        log(f"[{name}] no tree up to N'={n_prime} "
            f"({total_distinct} distinct structures tested so far)")

    info = {
        "status": "no_chordal_fine_graining",
        "bound_N_prime": n + bound,
        "distinct_structures_tested": total_distinct,
        "boundary_restriction": "leaves only",
        "qualifier": (f"BOUNDED: no chordal fine-graining of s={name} found up to "
                      f"N'={n + bound} across {total_distinct} distinct (pynauty-"
                      f"canonical) leaf-boundary tree structures with <= {n_bulk_max} "
                      f"bulk vertices. NOT a proof that no tree realization exists; "
                      f"NOT a statement about realizability (the ray is holographic). "
                      f"Evidence toward a strong-tree-conjecture counterexample, "
                      f"bounded by this enumeration."),
    }
    log(f"[{name}] no chordal fine-graining up to N'={n + bound} "
        f"({total_distinct} distinct structures). BOUNDED — not a non-existence claim.")
    return None, info

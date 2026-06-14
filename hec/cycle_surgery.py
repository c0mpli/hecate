"""hec/cycle_surgery.py — targeted entropy-preserving surgery to turn a
cyclic realization of a ray into a TREE one (or report bounded failure).

search.py localized all remaining hardness to the surviving-bulk-cycle
subclass (C5 rays 10, 17; n=6 orbits 111, 207). This tool attacks exactly
that structure with the EXACT entropy-preserving graph operations of
arXiv:2204.00075 §graph-operations — directed surgery, not blind search.

The moves (each preserves every one of the 2^n-1 entropies exactly; proven
analytically, and re-verified here in Fraction arithmetic after every step):
  Δ→Y  (lem:triop): triangle {i,j,k} -> new center σ with
        w_σi = w_ij + w_ik,  w_σj = w_ij + w_jk,  w_σk = w_ik + w_jk.
        Removes a 3-cycle: cyclomatic − 1.
  Y→Δ  (inverse): degree-3 bulk σ -> triangle, w_ij = (w_σi+w_σj−w_σk)/2,…
        Valid iff the triangle inequalities hold. cyclomatic + 1 (enabling).
  series: degree-2 bulk vertex between a,b with legs w1,w2 -> edge a-b of
        weight min(w1, w2). (neutral)
  parallel: two edges a-b -> one of weight w1 + w2. (cyclomatic − 1)
  prune: degree-1 bulk vertex (pendant) -> removed. (neutral)
  boundary split: a boundary vertex split into two same-party copies with its
        edges partitioned; exact (each entropy's cut is unchanged), and it
        breaks a boundary-incident cycle. (cyclomatic − 1 when it separates a
        cycle's two edges)

HARD RULES:
  1. SUCCESS = a forest realization (cyclomatic 0) still realizing the ray ->
     self-certifying cert (verified:true, exact, full vector). Answers the
     2024 paper's open question affirmatively for that orbit.
  2. FAILURE = "no entropy-preserving move sequence reduced the bulk cycle
     under <move set, node/depth bound>". This is BOUNDED — never a proof of
     non-existence, never "non-realizable". Logged with that exact qualifier.
  3. Floats may order moves; only exact Fraction arithmetic certifies a move
     preserved the ray (we verify the full vector after every move).
"""

from __future__ import annotations

import heapq
import itertools
import json
import pathlib
from fractions import Fraction

import networkx as nx

from hec.entropy import entropy_vector_labeled
from hec.subsets import vector_from_paper, vector_to_paper

REPORTS = pathlib.Path(__file__).resolve().parent.parent / "reports" / "realizations"


# --------------------------------------------------------------- graph utils

def cyclomatic(G):
    if G.number_of_nodes() == 0:
        return 0
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


def is_bulk(v, party):
    return v not in party


def _fresh_bulk(G, prefix="s"):
    i = 0
    while f"{prefix}{i}" in G:
        i += 1
    return f"{prefix}{i}"


def _add_w(G, a, b, w):
    """Add edge a-b of weight w, summing into an existing edge (parallel)."""
    if a == b:
        return
    if G.has_edge(a, b):
        G[a][b]["capacity"] += w
    else:
        G.add_edge(a, b, capacity=w)


def _W(G, a, b):
    return G[a][b]["capacity"]


# --------------------------------------------------------------- exact moves

def normalize(G, party):
    """Apply the neutral/reducing reductions (prune, series, parallel) to a
    fixpoint. Exact and size-reducing; canonicalizes a state before branching.
    (parallel edges are already summed by _add_w, so they never persist.)"""
    G = G.copy()
    changed = True
    while changed:
        changed = False
        # prune degree-1 bulk (pendant internal vertex contributes 0 to cuts)
        for v in list(G.nodes):
            if is_bulk(v, party) and G.degree(v) == 1:
                G.remove_node(v)
                changed = True
        # series: degree-2 bulk -> single edge of min weight
        for v in list(G.nodes):
            if is_bulk(v, party) and G.degree(v) == 2:
                (a, b) = list(G[v])
                w = min(_W(G, v, a), _W(G, v, b))
                G.remove_node(v)
                _add_w(G, a, b, w)
                changed = True
                break
        # drop any zero-weight edges
        for a, b, d in list(G.edges(data=True)):
            if d["capacity"] == 0:
                G.remove_edge(a, b)
                changed = True
    return G


def moves_delta_y(G, party):
    """Δ→Y on each triangle. Always valid; cyclomatic − 1."""
    seen = set()
    for a, b in list(G.edges):
        for c in set(G[a]) & set(G[b]):
            tri = frozenset((a, b, c))
            if tri in seen or len(tri) < 3:
                continue
            seen.add(tri)
            i, j, k = tuple(tri)
            H = G.copy()
            wij, wik, wjk = _W(H, i, j), _W(H, i, k), _W(H, j, k)
            H.remove_edge(i, j)
            H.remove_edge(i, k)
            H.remove_edge(j, k)
            s = _fresh_bulk(H)
            _add_w(H, s, i, wij + wik)
            _add_w(H, s, j, wij + wjk)
            _add_w(H, s, k, wik + wjk)
            yield H, dict(party), f"Δ→Y {i},{j},{k}"


def moves_y_delta(G, party):
    """Y→Δ on each degree-3 bulk vertex whose star obeys the triangle
    inequalities. cyclomatic + 1 (enabling move for cycles with no triangle)."""
    for s in list(G.nodes):
        if not is_bulk(s, party) or G.degree(s) != 3:
            continue
        i, j, k = list(G[s])
        wsi, wsj, wsk = _W(G, s, i), _W(G, s, j), _W(G, s, k)
        wij = Fraction(wsi + wsj - wsk, 1) / 2
        wik = Fraction(wsi + wsk - wsj, 1) / 2
        wjk = Fraction(wsj + wsk - wsi, 1) / 2
        if wij < 0 or wik < 0 or wjk < 0:
            continue
        H = G.copy()
        H.remove_node(s)
        for (a, b, w) in ((i, j, wij), (i, k, wik), (j, k, wjk)):
            if w:
                _add_w(H, a, b, w)
        yield H, dict(party), f"Y→Δ {s}"


def moves_boundary_split(G, party, n, max_branch=6):
    """Split a boundary vertex on a cycle into two same-party copies,
    partitioning its edges so a cycle's two edges land on different copies.
    Exact (every cut unchanged); breaks a boundary-incident cycle."""
    cyc_vs = set()
    for cyc in nx.cycle_basis(G):
        cyc_vs.update(cyc)
    count = 0
    for v in list(G.nodes):
        if is_bulk(v, party) or v not in cyc_vs or G.degree(v) < 2:
            continue
        nbrs = list(G[v])
        # try splits that separate two neighbors (the cycle's two arms)
        for a, b in itertools.combinations(nbrs, 2):
            rest = [x for x in nbrs if x not in (a, b)]
            # group a-side vs b-side; scatter the rest deterministically
            for mask in range(1 << len(rest)) if len(rest) <= 3 else [0]:
                g1 = [a] + [rest[t] for t in range(len(rest)) if mask >> t & 1]
                g2 = [b] + [rest[t] for t in range(len(rest)) if not mask >> t & 1]
                H = G.copy()
                p = dict(party)
                v2 = f"{party[v]}#{_fresh_bulk(H, 'c')}"
                p[v2] = party[v]
                H.add_node(v2)
                for w in g2:
                    cap = _W(H, v, w)
                    H.remove_edge(v, w)
                    _add_w(H, v2, w, cap)
                yield H, p, f"split {v}->({v},{v2})"
                count += 1
                if count >= max_branch:
                    return


def all_breaking_moves(G, party, n, allow_y_delta):
    yield from moves_delta_y(G, party)
    yield from moves_boundary_split(G, party, n)
    if allow_y_delta:
        yield from moves_y_delta(G, party)


# --------------------------------------------------------------- exact verify

def realizes(G, party, n, target):
    """Exact: does G (current weights) realize `target` exactly?"""
    try:
        return entropy_vector_labeled(G, n, party) == target
    except Exception:
        return False


# --------------------------------------------------------------- canonical key

def canon_key(G, party):
    """Iso-invariant key (parties as colors, bulk anonymous, weights encoded by
    subdividing each edge with a weight-colored midpoint). Dedups search
    states up to bulk relabeling and party-copy permutation."""
    try:
        import pynauty
    except Exception:
        # fallback: weak content key (still correct, just less dedup)
        return (cyclomatic(G), G.number_of_edges(),
                tuple(sorted(str(party.get(v, "b")) + str(G.degree(v)) for v in G)))
    nodes = list(G.nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    edges = [(idx[a], idx[b], d["capacity"]) for a, b, d in G.edges(data=True)]
    weights = sorted({w for _, _, w in edges})
    wcls = {w: i for i, w in enumerate(weights)}
    nv = len(nodes) + len(edges)
    adj = {i: [] for i in range(nv)}
    groups = {}
    for v in nodes:
        groups.setdefault(("p", party.get(v, "_bulk")), set()).add(idx[v])
    wgroup = {i: set() for i in range(len(weights))}
    for e, (a, b, w) in enumerate(edges):
        mid = len(nodes) + e
        adj[a].append(mid)
        adj[b].append(mid)
        wgroup[wcls[w]].add(mid)
    coloring = [s for s in groups.values()] + [wgroup[i] for i in range(len(weights))]
    coloring = [c for c in coloring if c]
    g = pynauty.Graph(nv, directed=False, adjacency_dict=adj, vertex_coloring=coloring)
    return (tuple(str(w) for w in weights), pynauty.certificate(g))


# --------------------------------------------------------------- the search

def surgery(seed_G, seed_party, n, name, target=None,
            max_nodes=4000, max_depth=30, y_delta_depth=8, out_dir=REPORTS,
            log=print):
    """Directed best-first surgery toward a forest. Returns (cert_path, info).
    cert_path is None on bounded failure; info carries the honest summary."""
    G0 = seed_G.copy()
    party0 = dict(seed_party)
    tgt = target or entropy_vector_labeled(G0, n, party0)
    assert realizes(G0, party0, n, tgt), "seed does not realize the target"

    G0 = normalize(G0, party0)
    if not realizes(G0, party0, n, tgt):
        # normalization must be exact; if not, refuse to proceed
        raise AssertionError("normalize changed the entropy vector — bug")

    if cyclomatic(G0) == 0:
        return _emit(name, n, G0, party0, tgt, ["(seed normalizes to a forest)"],
                     out_dir, log), {"status": "tree", "steps": 0}

    start_key = canon_key(G0, party0)
    # priority: (cyclomatic, edges, depth)
    heap = [(cyclomatic(G0), G0.number_of_edges(), 0, 0, G0, party0, [])]
    seen = {start_key}
    nodes = 0
    counter = 1
    best = (cyclomatic(G0), 0)
    while heap and nodes < max_nodes:
        kap, _, depth, _, G, party, trail = heapq.heappop(heap)
        nodes += 1
        if kap < best[0]:
            best = (kap, depth)
        allow_yd = depth < y_delta_depth
        for H, p, desc in all_breaking_moves(G, party, n, allow_yd):
            Hn = normalize(H, p)
            if not realizes(Hn, p, n, tgt):
                continue  # rule 3: reject any move that perturbs the vector
            k = canon_key(Hn, p)
            if k in seen:
                continue
            seen.add(k)
            new_trail = trail + [desc]
            if cyclomatic(Hn) == 0:
                return _emit(name, n, Hn, p, tgt, new_trail, out_dir, log), \
                    {"status": "tree", "steps": len(new_trail), "nodes": nodes}
            if depth + 1 <= max_depth:
                heapq.heappush(heap, (cyclomatic(Hn), Hn.number_of_edges(),
                                      depth + 1, counter, Hn, p, new_trail))
                counter += 1
    log(f"[{name}] no entropy-preserving sequence reduced the bulk cycle to a "
        f"tree under this move set and bound (nodes={nodes}, max_depth={max_depth}, "
        f"best cyclomatic reached={best[0]}). BOUNDED result — NOT a proof that "
        f"no tree realization exists.")
    return None, {"status": "no_reduction", "nodes": nodes,
                  "best_cyclomatic": best[0], "max_depth": max_depth}


def _emit(name, n, G, party, tgt, trail, out_dir, log):
    out_dir.mkdir(parents=True, exist_ok=True)
    assert entropy_vector_labeled(G, n, party) == tgt and nx.is_forest(G)
    from functools import reduce
    from math import gcd, lcm

    # integerize weights (Y→Δ can introduce halves) before writing the cert
    dens = [Fraction(d["capacity"]).denominator for _, _, d in G.edges(data=True)]
    L = lcm(*dens) if dens else 1
    Gi = nx.Graph()
    Gi.add_nodes_from(G.nodes)
    for u, v, d in G.edges(data=True):
        w = Fraction(d["capacity"]) * L
        assert w.denominator == 1
        if w:
            Gi.add_edge(u, v, capacity=int(w))
    realized = entropy_vector_labeled(Gi, n, party)  # integer now
    paper = vector_to_paper(realized, n)
    g = reduce(gcd, (int(x) for x in paper if x)) or 1
    if n == 6 and name in ("111", "207"):
        what = (f"TREE realization of bulk-cycle orbit s={name} (n=6) via "
                f"entropy-preserving Δ-Y surgery — answers the open question of "
                f"arXiv:2412.15364 affirmatively for this orbit")
    else:
        what = (f"tree realization of orbit s={name} (n={n}) via Δ-Y surgery "
                f"(tool validation; for n=5 such trees are already known, "
                f"arXiv:2204.00075 fig. N5trees)")
    cert = {
        "what": what,
        "engine": "hec.cycle_surgery (exact graph operations, arXiv:2204.00075)",
        "moves": trail,
        "scale": g,
        "edges": [[str(u), str(v), int(d["capacity"])] for u, v, d in Gi.edges(data=True)],
        "party": {str(v): party[v] for v in party},
        "is_forest": True,
        "cyclomatic": 0,
        "realized_vector": [int(x) for x in paper],
        "verified": True,
        "verify": "hec.entropy.entropy_vector_labeled(G, n, party) == realized_vector (exact)",
    }
    path = out_dir / f"n{n}_s{name}_TREE_surgery.json"
    path.write_text(json.dumps(cert, indent=2))
    log(f"[{name}] SUCCESS: tree realization in {len(trail)} moves -> {path.name}")
    return path

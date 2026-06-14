"""hec/search.py — overnight keep/discard search for the bulk-cycle problem.

Track A for the TWO bulk-cycle orbits s=111 and s=207 of arXiv:2412.15364
(graphERs footnote): their known holographic realizations contain a bulk
cycle, and whether tree-topology equivalents exist is an explicit open
question. This loop searches for a TREE (forest) realization.

Shape borrowed from karpathy/autoresearch — a keep/discard loop with a human
policy block — but with NO neural net: the "metric" is our exact verifier,
not a training loss. Mapping:
    autoresearch train.py (mutated artifact)  -> a candidate graph
    autoresearch 5-min val_bpb (the metric)   -> exact LP fit + ray-match
    autoresearch program.md (human policy)    -> the POLICY dict below
    autoresearch keep-if-improved             -> keep-if-lower-score, exact gate

Core idea (why this can work where blind tree-annealing failed at 1/8): seed
from a graph that ALREADY realizes the ray (the published cyclic model) and
walk entropy-preserving moves (Δ-Y, vertex splits) that reduce the cyclomatic
number, with the LP fitter re-certifying realization at every step. The
search stays on the "realizes-the-ray" manifold and drives cycles -> 0.

THREE HARD RULES (non-negotiable):
  1. Floats may SCORE/RANK candidates; only exact Fraction arithmetic
     (hec.tree_search._certify_labeled, via fit_tree_weights) may CERTIFY a
     hit. A found tree is valid only with a recorded exact match.
  2. SUCCESS = a found tree/forest realization, self-certifying: a full
     certificate to reports/realizations/ with verified:true and the
     realized 63-vector (same standard as n6_s181_minimal.json).
  3. FAILURE (loop ends, no tree) IS NOT EVIDENCE OF ANYTHING. The log says
     only "no tree found under <policy, budget>", never "no tree exists".
     Exclusion is the fine-graining machinery's job, not this loop's.
"""

from __future__ import annotations

import json
import math
import pathlib
import time
from fractions import Fraction

import networkx as nx

from hec.entropy import entropy_vector_labeled
from hec.subsets import vector_from_paper, vector_to_paper
from hec.tree_search import fit_tree_weights

# ======================================================================
# SEARCH POLICY  — the "program.md".  A human edits ONLY this block.
# Mechanics below read from it; keep policy and mechanics separate.
# ======================================================================
POLICY = {
    # budget per search() call (whichever is hit first)
    "budget_iters": 4000,
    "budget_seconds": 1200,
    # verifier effort: cheap scoring vs careful success-confirmation
    "score_attempts": 2,         # LP fits per candidate when ranking
    "score_descents": 10,        # LP descents per fit (ranking)
    "confirm_attempts": 8,       # LP fits to confirm a near-forest candidate
    "confirm_descents": 60,
    # annealing accept-worse schedule on the score (lower = better)
    "anneal_t0": 60.0,
    "anneal_t1": 2.0,
    # restart from a fresh seed after this many non-improving candidates
    "restart_stagnation": 250,
    # mutation operator weights (relative; the loop normalizes)
    "mutation_weights": {
        "split_vertex": 4.0,     # the workhorse cycle-breaker
        "split_purifier": 3.0,   # C5 ladder showed split-purifier is the hard case
        "delta_y": 2.0,          # 3-cycle -> star (entropy-preserving topology)
        "y_delta": 0.5,          # star -> 3-cycle (diversify / escape)
        "remove_edge": 2.0,      # drop a redundant cycle edge (refit must hold)
        "merge_bulk": 1.0,       # contract degree-2 / prune degree-1 bulk
        "add_edge": 0.5,         # diversify
    },
    # bias edge/vertex picks toward cycle members
    "cycle_bias": 0.8,
    # seed mix: how many random split-tree seeds to add alongside cyclic seeds
    "random_seeds": 3,
    "log_every": 50,
}
# ======================================================================

REPORTS = pathlib.Path(__file__).resolve().parent.parent / "reports" / "realizations"
SEEDS_FILE = pathlib.Path(__file__).resolve().parent.parent / "data" / "targets" / "bulk_cycle_seeds.json"


# ---------------------------------------------------------------- helpers

def cyclomatic(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


def _labels(n):
    return list(range(n)) + ["O"]


def _bulk_nodes(G, party):
    return [v for v in G.nodes if v not in party]


def _next_bulk(G):
    k = 0
    while f"k{k}" in G:
        k += 1
    return f"k{k}"


def _cycle_vertices(G):
    vs = set()
    for cyc in nx.cycle_basis(G):
        vs.update(cyc)
    return vs


def graph_from_edges(edges, n):
    """edge list (u, v, w) with int parties 0..n-1, 'O', bulk strings ->
    (G, party) with identity party labels for the boundary."""
    G = nx.Graph()
    party = {}
    for lab in _labels(n):
        G.add_node(lab)
        party[lab] = lab
    for u, v, w in edges:
        G.add_edge(u, v, capacity=int(w))
    return G, party


def labels_present(party, n):
    return set(party.values()) == set(_labels(n))


# ---------------------------------------------------------------- verifier

def _current_weights_cert(G, party, n, target):
    """If the graph's CURRENT weights already realize the ray exactly (a
    multiple of target), return the integer, zero-edge-pruned graph and its
    scale. Cheap exact check — vital for seeds and weight-preserving moves,
    which already realize the ray and must not be re-fit from scratch."""
    caps = [d["capacity"] for _, _, d in G.edges(data=True)]
    if not caps:
        return None
    fr = [c if isinstance(c, Fraction) else Fraction(c) for c in caps]
    from math import lcm
    L = lcm(*(c.denominator for c in fr)) if fr else 1
    Gi = nx.Graph()
    Gi.add_nodes_from(G.nodes)
    for u, v, d in G.edges(data=True):
        w = Fraction(d["capacity"]) * L
        if w.denominator != 1:
            return None
        if w:
            Gi.add_edge(u, v, capacity=int(w))
    S = entropy_vector_labeled(Gi, n, party)
    s1 = target[1] if target.get(1) else next(v for v in target.values() if v)
    g1 = S.get(1) or next((S[m] for m in target if S[m]), 0)
    if not g1 or g1 % s1:
        return None
    k = g1 // s1
    if k >= 1 and all(S[m] == k * target[m] for m in target):
        return Gi, k
    return None


def evaluate(G, party, n, target, rng, policy, confirm=False):
    """Score a candidate. Returns (score, cert | None, success).

    score: lower is better. A candidate that realizes the ray scores 100*κ
    (κ = cyclomatic of the certified, zero-edge-pruned graph); one that does
    not scores 1000 + best_slack. SUCCESS = realizes the ray AND κ == 0
    (a tree/forest). The cert is exact (current weights, or fit_tree_weights
    -> _certify_labeled — both exact-verified).
    """
    cur = _current_weights_cert(G, party, n, target)
    if cur is not None:
        Gi, scale = cur
        kap = cyclomatic(Gi)
        return 100.0 * kap, (Gi, scale), (kap == 0)
    attempts = policy["confirm_attempts"] if confirm else policy["score_attempts"]
    descents = policy["confirm_descents"] if confirm else policy["score_descents"]
    best_cert, best_slack = None, float("inf")
    for _ in range(attempts):
        hit, slack = fit_tree_weights(G, party, n, target, rng,
                                      descents=descents, report=True)
        best_slack = min(best_slack, slack)
        if hit is not None:
            best_cert = hit
            break
    if best_cert is None:
        return 1000.0 + best_slack, None, False
    Gi, scale = best_cert
    kap = cyclomatic(Gi)
    return 100.0 * kap, (Gi, scale), (kap == 0)


# ---------------------------------------------------------------- mutations

def _split_vertex(G, party, rng, cyc_vs, prefer):
    cands = [v for v in G.nodes if G.degree(v) >= 2]
    if prefer == "purifier":
        pc = [v for v in cands if party.get(v) == "O"]
        cands = pc or cands
    if cyc_vs and rng.random() < 0.7:
        cc = [v for v in cands if v in cyc_vs]
        cands = cc or cands
    if not cands:
        return None
    v = rng.choice(cands)
    nbr_edges = [(w, G[v][w]["capacity"]) for w in G[v]]
    rng.shuffle(nbr_edges)
    cut = rng.randint(1, len(nbr_edges) - 1)
    g2 = nbr_edges[cut:]
    H = G.copy()
    p = dict(party)
    if v in party:
        v2 = f"{party[v]}#{rng.randrange(1 << 30)}"
        p[v2] = party[v]
    else:
        v2 = _next_bulk(H)
    H.add_node(v2)
    for w, cap in g2:
        H.remove_edge(v, w)
        H.add_edge(v2, w, capacity=cap)
    if rng.random() < 0.5:
        H.add_edge(v, v2, capacity=1)
    return H, p


def _delta_y(G, party, rng):
    tris = []
    for a, b in G.edges:
        common = set(G[a]) & set(G[b])
        for c in common:
            tris.append((a, b, c))
    if not tris:
        return None
    a, b, c = rng.choice(tris)
    H = G.copy()
    for x, y in [(a, b), (b, c), (a, c)]:
        if H.has_edge(x, y):
            H.remove_edge(x, y)
    y = _next_bulk(H)
    for x in (a, b, c):
        H.add_edge(y, x, capacity=1)
    return H, dict(party)


def _y_delta(G, party, rng):
    cands = [v for v in G.nodes if v not in party and G.degree(v) == 3]
    if not cands:
        return None
    y = rng.choice(cands)
    a, b, c = list(G[y])
    H = G.copy()
    H.remove_node(y)
    for x, z in [(a, b), (b, c), (a, c)]:
        if not H.has_edge(x, z):
            H.add_edge(x, z, capacity=1)
    return H, dict(party)


def _remove_edge(G, party, rng, cyc_vs):
    edges = list(G.edges)
    if cyc_vs and rng.random() < 0.8:
        ce = [(u, v) for u, v in edges if u in cyc_vs and v in cyc_vs]
        edges = ce or edges
    if not edges:
        return None
    u, v = rng.choice(edges)
    H = G.copy()
    H.remove_edge(u, v)
    return H, dict(party)


def _merge_bulk(G, party, rng):
    bulks = _bulk_nodes(G, party)
    d1 = [b for b in bulks if G.degree(b) == 1]
    d2 = [b for b in bulks if G.degree(b) == 2]
    if d1 and rng.random() < 0.5:
        H = G.copy()
        H.remove_node(rng.choice(d1))
        return H, dict(party)
    if d2:
        b = rng.choice(d2)
        a, c = list(G[b])
        H = G.copy()
        H.remove_node(b)
        if a != c and not H.has_edge(a, c):
            H.add_edge(a, c, capacity=1)
        return H, dict(party)
    return None


def _add_edge(G, party, rng):
    nodes = list(G.nodes)
    for _ in range(8):
        u, v = rng.sample(nodes, 2)
        if not G.has_edge(u, v):
            H = G.copy()
            H.add_edge(u, v, capacity=1)
            return H, dict(party)
    return None


def mutate(G, party, n, rng, policy):
    cyc_vs = _cycle_vertices(G) if rng.random() < policy["cycle_bias"] else set()
    ops = list(policy["mutation_weights"].items())
    names = [o[0] for o in ops]
    weights = [o[1] for o in ops]
    for _ in range(12):
        op = rng.choices(names, weights=weights)[0]
        if op == "split_vertex":
            res = _split_vertex(G, party, rng, cyc_vs, prefer=None)
        elif op == "split_purifier":
            res = _split_vertex(G, party, rng, cyc_vs, prefer="purifier")
        elif op == "delta_y":
            res = _delta_y(G, party, rng)
        elif op == "y_delta":
            res = _y_delta(G, party, rng)
        elif op == "remove_edge":
            res = _remove_edge(G, party, rng, cyc_vs)
        elif op == "merge_bulk":
            res = _merge_bulk(G, party, rng)
        else:
            res = _add_edge(G, party, rng)
        if res is None:
            continue
        H, p = res
        if H.number_of_edges() == 0 or not labels_present(p, n):
            continue
        if not nx.is_connected(H):
            # allow forests but not stray isolated bulk vertices
            H.remove_nodes_from([v for v in list(H.nodes)
                                 if H.degree(v) == 0 and v not in p])
        return H, p
    return None


# ---------------------------------------------------------------- seeds

def load_seeds(name, n, rng, policy):
    """Seeds for `name`: cyclic published graph(s) + random split-trees.

    C5 rays (n=5): from hec.c5_graphs. 111/207: from data/targets/
    bulk_cycle_seeds.json if present (extracted by scripts/extract_bulk_seeds.py),
    else a flag is set and only random seeds are used (the ladder still runs).
    Returns (seeds, missing_cyclic: bool).
    """
    cyclic = []
    missing = False
    if name.startswith("c5_"):
        from hec.c5_graphs import C5_PUBLISHED_GRAPHS
        k = int(name[3:])
        cyclic.append(graph_from_edges(C5_PUBLISHED_GRAPHS[k], n))
    elif name in ("111", "207"):
        if SEEDS_FILE.exists():
            data = json.loads(SEEDS_FILE.read_text())
            if name in data.get("seeds", {}):
                edges = [tuple(e) for e in data["seeds"][name]["edges"]]
                edges = [(_relabel(u), _relabel(v), w) for u, v, w in edges]
                cyclic.append(graph_from_edges(edges, n))
            else:
                missing = True
        else:
            missing = True
    # random split-tree seeds: diversification only. They are NOT realizing
    # starting points, so when a cyclic seed exists they must NOT dilute it on
    # restart (the bug that cost the first ladder run several easy rays).
    from hec.tree_search import seed_tree
    rand = [seed_tree(n, rng, extra_bulk=rng.randint(1, 3))
            for _ in range(policy["random_seeds"])]
    return cyclic, rand, missing


def _relabel(x):
    if isinstance(x, str) and x in ("0", "1", "2", "3", "4", "5"):
        return int(x)
    return x


# ---------------------------------------------------------------- the loop

def _write_cert(name, n, Gi, scale, party, out_dir, policy):
    out_dir.mkdir(parents=True, exist_ok=True)
    realized = entropy_vector_labeled(Gi, n, party)
    cert = {
        "what": f"TREE (forest) realization of orbit s={name} (n={n}) — "
                f"resolves the bulk-cycle open question of arXiv:2412.15364 "
                f"affirmatively for this orbit",
        "engine": "hec.search keep/discard loop (entropy-preserving moves on a "
                  "cyclic seed, exact LP-certified)",
        "scale": scale,
        "edges": [[str(u), str(v), d["capacity"]] for u, v, d in Gi.edges(data=True)],
        "party": {str(v): (party[v] if not isinstance(party[v], int) else party[v])
                  for v in party},
        "is_forest": bool(nx.is_forest(Gi)),
        "cyclomatic": cyclomatic(Gi),
        "realized_vector": list(vector_to_paper(realized, n)),
        "verified": True,
        "verify": "hec.entropy.entropy_vector_labeled(G, n, party) == scale * ray",
        "policy": policy,
    }
    path = out_dir / f"n{n}_s{name}_TREE.json"
    path.write_text(json.dumps(cert, indent=2))
    return path


def search(target, n, name, rng, policy=POLICY, log=print, out_dir=REPORTS):
    """Search for a tree realization of `target`. Returns the certificate path
    on success, else None. target: paper-order tuple or {mask:int}."""
    tgt = target if isinstance(target, dict) else vector_from_paper(target, n)
    cyclic, rand, missing = load_seeds(name, n, rng, policy)
    if missing:
        log(f"[{name}] NOTE: no cyclic seed available (stub) — running with "
            f"random split-tree seeds only; Δ-Y from the published cycle is "
            f"the intended path. See scripts/extract_bulk_seeds.py.")

    best_real = [None]  # (kappa, G, party) — lowest-κ realizing graph seen

    def fresh():
        # restarts strongly prefer a realizing start: the cyclic seed, or the
        # best realizing graph found so far (retry the cycle-break with new
        # RNG). Random trees are last resort / the no-cyclic-seed case.
        r = rng.random()
        if best_real[0] is not None and r < 0.4:
            _, G0, p0 = best_real[0]
        elif cyclic and r < 0.9:
            G0, p0 = cyclic[rng.randrange(len(cyclic))]
        else:
            pool = rand or cyclic
            G0, p0 = pool[rng.randrange(len(pool))]
        return G0.copy(), dict(p0)

    def note_real(cert):
        kap = cyclomatic(cert[0])
        if best_real[0] is None or kap < best_real[0][0]:
            best_real[0] = (kap, cur_G.copy(), dict(cur_p))

    cur_G, cur_p = fresh()
    cur_score, cur_cert, success = evaluate(cur_G, cur_p, n, tgt, rng, policy)
    if cur_cert is not None:
        note_real(cur_cert)
    if success:
        Gi, scale = cur_cert
        path = _write_cert(name, n, Gi, scale, cur_p, out_dir, policy)
        log(f"[{name}] SUCCESS at seed: tree realization -> {path.name}")
        return path
    best_score = cur_score
    stagn = 0
    t0 = time.perf_counter()
    it = 0
    while it < policy["budget_iters"] and time.perf_counter() - t0 < policy["budget_seconds"]:
        it += 1
        frac = it / policy["budget_iters"]
        T = policy["anneal_t0"] * (1 - frac) + policy["anneal_t1"] * frac
        mut = mutate(cur_G, cur_p, n, rng, policy)
        if mut is None:
            stagn += 1
        else:
            H, p = mut
            score, cert, success = evaluate(H, p, n, tgt, rng, policy)
            if cert is not None and not success and cyclomatic(cert[0]) <= 1:
                score2, cert2, success2 = evaluate(H, p, n, tgt, rng, policy, confirm=True)
                if success2:
                    score, cert, success = score2, cert2, True
            if success:
                Gi, scale = cert
                path = _write_cert(name, n, Gi, scale, p, out_dir, policy)
                log(f"[{name}] SUCCESS at iter {it} ({time.perf_counter()-t0:.0f}s, "
                    f"{it} candidates): tree realization -> {path.name}")
                return path
            accept = score < cur_score or rng.random() < math.exp(-(score - cur_score) / max(T, 1e-6))
            if accept:
                cur_G, cur_p, cur_score = H, p, score
                if cert is not None:
                    note_real(cert)
            if score < best_score:
                best_score = score
                stagn = 0
            else:
                stagn += 1
        if stagn >= policy["restart_stagnation"]:
            cur_G, cur_p = fresh()
            cur_score, c, _ = evaluate(cur_G, cur_p, n, tgt, rng, policy)
            if c is not None:
                note_real(c)
            stagn = 0
        if it % policy["log_every"] == 0:
            kb = best_real[0][0] if best_real[0] else "?"
            log(f"[{name}] iter {it} | best_score {best_score:.1f} | "
                f"best realizing κ={kb} | cur {cur_score:.1f} | "
                f"{time.perf_counter()-t0:.0f}s")
    log(f"[{name}] no tree found under this policy/budget "
        f"({it} candidates, {time.perf_counter()-t0:.0f}s). "
        f"NOT evidence that no tree exists.")
    return None

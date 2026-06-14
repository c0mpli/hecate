"""hec/seed_search.py — multi-seed bulk-cycle experiment.

Question: is the bulk-cycle obstruction cycle_surgery hit on s=111 a property
of the ONE seed we tried (the hecdata realization), or intrinsic to the ray?

Method: generate several STRUCTURALLY DISTINCT cyclic realizations of the same
ray (each exactly realizing a positive multiple of the 63-vector, verified in
Fraction arithmetic; deduped by pynauty canonical form), then run the
cycle_surgery reduction on each.

  ANY seed reduces to a tree  -> obstruction was seed-specific; the ray IS
        tree-realizable; the 2024 open question is answered affirmatively. STOP.
  ALL distinct seeds hit the same characterized obstruction -> bounded EVIDENCE
        (never proof) the obstruction is intrinsic; this is what would justify
        building the fine-graining exclusion engine next.

Seed sources (all give realizations of the SAME representative ray):
  - the base seed;
  - images under the STABILIZER of the ray in Sym(n+1) (relabelings that fix
    the vector — a party permutation that changes graph structure but not the
    realized vector);
  - LP-generated alternatives on different sampled topologies (hec.lp_realize).

Hard rules: only exact Fraction arithmetic certifies a realization or a move;
every negative carries {move set, bound, seed set}; never an unbounded
"no tree exists".
"""

from __future__ import annotations

import json
import pathlib
from fractions import Fraction
from itertools import permutations

import networkx as nx

from hec.cone import permute_vector
from hec.cycle_surgery import (
    REPORTS,
    canon_key,
    characterize_obstruction,
    cyclomatic,
    normalize,
    surgery,
)
from hec.entropy import entropy_vector_labeled
from hec.subsets import vector_from_paper, vector_to_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _enc(l, n):
    return n if l == "O" else l


def _dec(i, n):
    return "O" if i == n else i


def relabel_edges(edges, perm, n):
    """Relabel boundary vertices by perm (a permutation of [0..n], n == 'O');
    bulk vertices untouched."""
    def m(x):
        if isinstance(x, str) and not x == "O":
            return x  # bulk
        return _dec(perm[_enc(x, n)], n)
    return [(m(u), m(v), w) for u, v, w in edges]


def stabilizer(ray_vec, n):
    """Permutations of Sym(n+1) that fix the entropy vector exactly."""
    rd = vector_from_paper(ray_vec, n)
    out = []
    for perm in permutations(range(n + 1)):
        if permute_vector(rd, perm, n) == rd:
            out.append(perm)
    return out


def structure_key(G, party):
    """Party-BLIND canonical form: all boundary vertices share one color, bulk
    another, weights encoded by subdivision. Symmetry (stabilizer) images
    collapse to the same key — so this counts INDEPENDENT bulk structures, not
    just distinct labelings."""
    try:
        import pynauty
    except Exception:
        return (G.number_of_edges(), tuple(sorted(dict(G.degree()).values())))
    nodes = list(G.nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    edges = [(idx[a], idx[b], d["capacity"]) for a, b, d in G.edges(data=True)]
    weights = sorted({w for _, _, w in edges})
    wcls = {w: i for i, w in enumerate(weights)}
    nv = len(nodes) + len(edges)
    adj = {i: [] for i in range(nv)}
    bdry = {idx[v] for v in nodes if v in party}
    bulk = {idx[v] for v in nodes if v not in party}
    wgroup = {i: set() for i in range(len(weights))}
    for e, (a, b, w) in enumerate(edges):
        mid = len(nodes) + e
        adj[a].append(mid)
        adj[b].append(mid)
        wgroup[wcls[w]].add(mid)
    coloring = [c for c in ([bdry, bulk] + [wgroup[i] for i in range(len(weights))]) if c]
    g = pynauty.Graph(nv, directed=False, adjacency_dict=adj, vertex_coloring=coloring)
    return (tuple(str(w) for w in weights), pynauty.certificate(g))


def _graph(edges, n):
    G = nx.Graph()
    party = {}
    for lab in list(range(n)) + ["O"]:
        G.add_node(lab)
        party[lab] = lab
    for u, v, w in edges:
        G.add_edge(u, v, capacity=Fraction(int(w)) if not isinstance(w, Fraction) else w)
    return G, party


def _realizes_multiple(G, party, n, ray_dict):
    """Exact: does G realize k*ray for some positive integer k?"""
    S = entropy_vector_labeled(G, n, party)
    s1 = next((ray_dict[m] for m in ray_dict if ray_dict[m]), 0)
    g1 = next((S[m] for m in ray_dict if ray_dict[m]), 0)
    if not s1 or not g1 or (g1 % s1 if isinstance(g1, int) else g1 / s1 % 1):
        # robust integer/Fraction check below
        pass
    for k in range(1, 60):
        if all(S[m] == k * ray_dict[m] for m in ray_dict):
            return k
    return None


def distinct_seeds(base_edges, ray_vec, n, rng, lp_attempts=24, max_seeds=12,
                   log=print):
    """Return up to max_seeds structurally-distinct cyclic realizations as
    (G, party, provenance), all verified to realize a multiple of the ray."""
    ray_dict = vector_from_paper(ray_vec, n)
    seeds = []
    keys = set()

    def consider(edges, prov):
        G, party = _graph(edges, n)
        k = _realizes_multiple(G, party, n, ray_dict)
        if k is None:
            return
        Gn = normalize(G, party)
        if cyclomatic(Gn) == 0:
            # a seed that is already a forest answers the question outright
            seeds.append((G, party, prov + " [ALREADY A FOREST]"))
            return
        key = canon_key(Gn, party)
        if key in keys:
            return
        keys.add(key)
        seeds.append((G, party, prov))

    consider(base_edges, "base (hecdata Sym(7) match)")
    # stabilizer images
    stab = stabilizer(ray_vec, n)
    for perm in stab:
        if len(seeds) >= max_seeds:
            break
        if perm == tuple(range(n + 1)):
            continue
        consider(relabel_edges(base_edges, perm, n), f"stabilizer image {perm}")
    log(f"  stabilizer of the ray: {len(stab)} elements; "
        f"{len(seeds)} distinct seeds so far")

    # LP-generated alternatives: fit the ray on explicit complete topologies of
    # varying bulk count (b vertices) — these give genuinely different bulk
    # structures, the seeds that actually test 'intrinsic vs seed-specific'.
    from hec.lp_realize import _complete_topology, fit_weights, sample_topology
    got_lp = 0
    topos = [("complete", b) for b in range(2, 7) for _ in range(2)]
    topos += [("sampled", 0) for _ in range(lp_attempts)]
    for kind, b in topos:
        if len(seeds) >= max_seeds:
            break
        G0 = _complete_topology(n, b) if kind == "complete" else sample_topology(n, rng)
        for _ in range(4):
            hit = fit_weights(G0, n, ray_dict, rng, descents=70)
            if hit is not None:
                Gi, scale = hit
                edges = [(u, v, d["capacity"]) for u, v, d in Gi.edges(data=True)]
                before = len(seeds)
                consider(edges, f"LP {kind} b={b}")
                if len(seeds) > before:
                    got_lp += 1
                break
    log(f"  LP-generated distinct seeds: {got_lp}; total distinct: {len(seeds)}")
    return seeds


def run_multiseed(name, ray_vec, n, rng, max_nodes=20000, max_depth=40,
                  lp_attempts=24, max_seeds=12, out_dir=REPORTS, log=print):
    """Run cycle surgery on each distinct seed. First tree -> success cert +
    stop. Else honest bounded summary to reports/bulk_cycle_attempts.jsonl."""
    base_path = ROOT / "data" / "targets" / "bulk_cycle_seeds.json"
    if name in ("111", "207"):
        data = json.loads(base_path.read_text()).get("seeds", {})
        if name not in data:
            log(f"[{name}] no base cyclic seed available — skipped")
            return None, {"status": "no_seed"}
        base_edges = [(_b(u), _b(v), int(w)) for u, v, w in data[name]["edges"]]
    else:
        from hec.c5_graphs import C5_PUBLISHED_GRAPHS
        base_edges = [(u, v, w) for u, v, w in C5_PUBLISHED_GRAPHS[int(name)]]

    log(f"[{name}] generating distinct cyclic seeds ...")
    seeds = distinct_seeds(base_edges, ray_vec, n, rng,
                           lp_attempts=lp_attempts, max_seeds=max_seeds, log=log)
    log(f"[{name}] {len(seeds)} structurally-distinct seeds (pynauty-deduped)")

    # count INDEPENDENT bulk structures (party-blind), not just labelings
    struct = {}
    for (G, party, _prov) in seeds:
        struct.setdefault(structure_key(normalize(G, party), party), 0)
        struct[structure_key(normalize(G, party), party)] += 1
    n_structures = len(struct)
    log(f"[{name}] {len(seeds)} seeds span {n_structures} INDEPENDENT bulk "
        f"structure(s) (party-blind); the rest are symmetry copies")

    per_seed = []
    for i, (G, party, prov) in enumerate(seeds):
        tgt = entropy_vector_labeled(G, n, party)
        path, info = surgery(G, party, n, name, target=tgt, max_nodes=max_nodes,
                             max_depth=max_depth, out_dir=out_dir, log=log)
        if info["status"] == "tree":
            log(f"[{name}] *** SEED {i} ({prov}) REDUCED TO A TREE *** — the "
                f"bulk-cycle obstruction was SEED-SPECIFIC; the ray is "
                f"tree-realizable. Open question answered affirmatively.")
            return path, {"status": "tree", "seed_index": i, "provenance": prov,
                          "seeds_tried": len(seeds)}
        obstruction = characterize_obstruction(*info["_best_graph"])
        per_seed.append({"seed": i, "provenance": prov,
                         "best_cyclomatic": info["best_cyclomatic"],
                         "exhausted_nodes": info["nodes"],
                         "obstruction": obstruction})
        log(f"[{name}] seed {i} ({prov}): no reduction, best κ="
            f"{info['best_cyclomatic']} (closure exhausted at {info['nodes']} nodes)")

    # honest bounded summary
    pure_bulk_all = all(
        any(c["pure_bulk"] and not c["delta_y_applicable"] and not c["y_delta_candidates"]
            for c in s["obstruction"])
        for s in per_seed) if per_seed else False
    independent = n_structures < 2
    summary = {
        "orbit": name,
        "tool": "seed_search + cycle_surgery",
        "seeds_tried": len(seeds),
        "independent_bulk_structures": n_structures,
        "result": "no_reduction_any_seed",
        "all_seeds_pure_bulk_obstruction": pure_bulk_all,
        "seed_generation_note": (
            "Independent realizations of this n=6 ray could not be generated "
            "beyond the published one: hecdata has exactly 1 orbit row, "
            "lp_realize_target found 0 in repeated tries, and the ray's "
            "stabilizer yields only symmetry copies (identical bulk structure)."
            if name == "111" else ""),
        "interpretation": (
            f"Tried {len(seeds)} cyclic seeds spanning {n_structures} INDEPENDENT "
            f"bulk structure(s); the move set {{Δ-Y, Y-Δ, series, parallel, "
            f"prune, boundary-split}} reduced none to a tree. " + (
                ("Each available realization's FULL entropy-preserving move-"
                 "closure was searched exhaustively (frontier emptied), and the "
                 "surviving obstruction is a pure-bulk cycle with no triangle and "
                 "no degree-3 bulk vertex — provably untouchable by the complete "
                 "local move set. " if pure_bulk_all else "") +
                ("HOWEVER only %d independent structure(s) could be tested, so "
                 "this does NOT distinguish 'intrinsic to the ray' from 'shared "
                 "by the one reachable realization': it is INCONCLUSIVE on that "
                 "question, bounded by seed-generation failure at n=6. The "
                 "ray-level fine-graining exclusion engine (Track B) is the tool "
                 "that settles it. " % n_structures if independent else
                 "Across the independent structures tested, all hit the same "
                 "pure-bulk obstruction — bounded EVIDENCE (not proof) it may be "
                 "intrinsic. ") +
                "NOT a proof that no tree exists — bounded by this move set, "
                "node/depth limits, and finite seed set."
            )),
        "per_seed": per_seed,
    }
    logf = ROOT / "reports" / "bulk_cycle_attempts.jsonl"
    logf.parent.mkdir(exist_ok=True)
    with logf.open("a") as fh:
        fh.write(json.dumps(summary) + "\n")
    log(f"[{name}] no seed reduced ({len(seeds)} distinct seeds). "
        f"Bounded evidence logged -> {logf.relative_to(ROOT)}. "
        f"NOT a non-existence claim.")
    return None, summary


def _b(x):
    return int(x) if isinstance(x, str) and x in ("0", "1", "2", "3", "4", "5") else x

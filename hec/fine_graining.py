"""hec/fine_graining.py — bounded fine-graining engine for NON-SIMPLE tree
realizability, the seed-independent successor to cycle_surgery.py.

Theorem chain (arXiv:2412.18018 -> 2512.18702 -> 2512.24490): a vector is
realizable by a (possibly non-simple) tree iff some party-splitting
FINE-GRAINING of it is realizable by a SIMPLE tree, i.e. (chordality iff) has
a chordal correlation-hypergraph line graph. So we work from the ENTROPY
VECTOR: split parties (up to a bound on added sub-parties N'), and look for a
refined vector that coarse-grains back to the target AND is chordal -> build
its simple tree (hec.tree_builder) and relabel the splits back -> a non-simple
tree for the target.

CORRECTNESS ANCHOR — coarse-graining (the deterministic direction,
arXiv:2512.18702 eq. ent-vec-cg): for a CG-map cg: refined labels -> original
labels (surjective; refined parties may merge, or map to the purifier =
traced out), the coarse-grained entropy of an original subset X is the refined
entropy of cg^{-1}(X):
        S_X = S'_{ cg^{-1}(X) }.
This module's `coarse_grain` implements exactly this and is validated by a
round-trip against the labeled-entropy ground truth (a non-simple tree's
refined vector coarse-grains to the labeled vector it realizes).

HARD RULES:
  1. The ONLY negative is BOUNDED: "no tree-able fine-graining up to N'=<k>".
     NEVER "non-realizable"/"no tree exists"/anything unbounded. (The ~1.4M
     vertex bound makes true exhaustion infeasible; 111 is holographic — this
     engine decides only the TREE question.)
  2. Every output records N', the enumeration strategy, the count of DISTINCT
     fine-grainings tested (canonicalized), and that each was tested in EXACT
     arithmetic. Floats may prune/order; only Fraction certifies.
  3. A chordal fine-graining found mid-search is a SUCCESS: build + certify the
     tree, stop.
"""

from __future__ import annotations

import networkx as nx

from hec.entropy import entropy_vector, entropy_vector_labeled
from hec.subsets import vector_from_paper, vector_to_paper


def coarse_grain(Sprime, cg_map, n_prime, n):
    """Coarse-grain a refined entropy vector to the original party set.

    Sprime: dict {mask over [n_prime] : value} (refined party subsets; purity
            implicit, refined purifier is the complement).
    cg_map: dict mapping each refined party p in 0..n_prime-1 to an original
            label in 0..n-1 or "O" (purifier = traced out). Surjective onto
            0..n-1.
    Returns: dict {mask over [n] : value} — the coarse-grained vector, with
    S_X = S'_{cg^{-1}(X)} for X a nonempty subset of original parties.
    """
    S = {}
    for I in range(1, 1 << n):
        Xprime = 0
        for p in range(n_prime):
            tgt = cg_map[p]
            if isinstance(tgt, int) and (I >> tgt) & 1:
                Xprime |= 1 << p
        if Xprime == 0:
            # cg^{-1}(X) empty -> entropy 0 (no refined party carries X)
            S[I] = 0
        else:
            S[I] = Sprime[Xprime]
    return S


def relabel_to_simple(G, party):
    """Turn a NON-simple labeled tree (a party — possibly the purifier — may
    label many leaves) into a genuinely SIMPLE refined tree: EVERY boundary
    vertex becomes its own distinct refined label, with exactly ONE designated
    the refined purifier. Extra purifier copies become refined PARTIES that the
    CG-map sends back to the original purifier (traced out). This is the
    correct fine-graining: a simple tree has one boundary vertex per refined
    party AND a single purifier.

    Returns (Gs, n_prime, cg_map, refined_pmap):
      Gs           simple refined tree (parties 0..n_prime-1, purifier 'O'),
      n_prime      number of refined parties,
      cg_map       {refined party index -> original label (int party or 'O')},
      refined_pmap party map for entropy_vector_labeled on Gs.
    """
    boundary = [v for v in G.nodes if v in party]
    pur_copies = [v for v in boundary if party[v] == "O"]
    others = [v for v in boundary if party[v] != "O"]
    if pur_copies:
        chosen_pur = pur_copies[0]
        refined_parties = others + pur_copies[1:]  # extra purifier copies -> parties->'O'
    else:
        chosen_pur = None
        refined_parties = others
    rp, cg = {}, {}
    for i, v in enumerate(refined_parties):
        rp[v] = i
        cg[i] = party[v]  # original party int, or 'O' for extra purifier copies
    n_prime = len(refined_parties)
    relabel = {}
    for v in G.nodes:
        if v in rp:
            relabel[v] = rp[v]
        elif v is chosen_pur:
            relabel[v] = "O"
        else:
            relabel[v] = v  # bulk
    Gs = nx.Graph()
    for a, b, d in G.edges(data=True):
        Gs.add_edge(relabel[a], relabel[b], capacity=d["capacity"])
    refined_pmap = {v: ("O" if v == "O" else v) for v in Gs.nodes if v == "O" or isinstance(v, int)}
    return Gs, n_prime, cg, refined_pmap


def refined_vector(Gs, n_prime, refined_pmap):
    """Entropy vector of the refined SIMPLE tree over its n_prime refined
    parties (single purifier 'O')."""
    return entropy_vector_labeled(Gs, n_prime, refined_pmap)


def certify_fine_graining(T, party, S_target, n, name, out_dir=None, log=print):
    """Given a NON-simple tree T (party map, possibly many leaves per party),
    certify it as a fine-graining realization of S_target: (i) it is a forest;
    (ii) its refined simple tree is CHORDAL (the theorem's certificate);
    (iii) the refined vector coarse-grains EXACTLY back to a multiple of
    S_target. Returns the cert dict (or None if it fails any check)."""
    import json
    import pathlib
    from functools import reduce
    from math import gcd

    from hec.chordality import simple_forest_realizable

    if not nx.is_forest(T):
        return None
    labeled = entropy_vector_labeled(T, n, party)
    s1 = next((S_target[m] for m in S_target if S_target[m]), 0)
    g1 = next((labeled[m] for m in S_target if S_target[m]), 0)
    scale = None
    for k in range(1, 60):
        if all(labeled[m] == k * S_target[m] for m in S_target):
            scale = k
            break
    if scale is None:
        return None
    Gs, n_prime, cg, rpmap = relabel_to_simple(T, party)
    Sprime = refined_vector(Gs, n_prime, rpmap)
    chord = simple_forest_realizable(Sprime, n_prime)
    back = coarse_grain(Sprime, cg, n_prime, n)
    if not (chord["chordal"] and back == labeled):
        return None  # would indicate a non-simple refined tree or lift bug
    paper = vector_to_paper(labeled, n)
    cert = {
        "what": (f"NON-SIMPLE TREE realization of orbit s={name} (n={n}) via "
                 f"bounded fine-graining — its refined simple tree (N'={n_prime}) "
                 f"is CHORDAL (arXiv:2512.24490 iff) and coarse-grains back to the "
                 f"ray exactly" + (
                     " — answers the bulk-cycle open question of arXiv:2412.15364 "
                     "affirmatively for this orbit" if n == 6 and name in ("111", "207")
                     else " (validation; C5 trees are known, arXiv:2204.00075)")),
        "engine": "hec.fine_graining (coarse-graining + chordality, exact)",
        "n_prime": n_prime,
        "cg_map": {str(p): cg[p] for p in cg},
        "refined_chordal": True,
        "scale": scale,
        "edges": [[str(u), str(v), int(d["capacity"])] for u, v, d in T.edges(data=True)],
        "party": {str(v): party[v] for v in party},
        "is_forest": True,
        "realized_vector": [int(x) for x in paper],
        "verified": True,
        "verify": ("entropy_vector_labeled(T)==scale*ray (exact); refined simple "
                   "tree chordal; coarse_grain(refined,cg)==entropy_vector_labeled(T)"),
    }
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"n{n}_s{name}_TREE_finegraining.json"
        path.write_text(json.dumps(cert, indent=2))
        cert["_path"] = str(path)
        log(f"[{name}] CERTIFIED fine-graining (N'={n_prime}, refined chordal) -> {path.name}")
    return cert


def fine_graining_realizable(name, S_target, n, bound, cyclic_seed=None,
                             out_dir=None, surgery_nodes=20000, log=print):
    """Bounded fine-graining decision for NON-simple tree realizability.

    Strategy (each success exact-certified via certify_fine_graining):
      0. base chordality — if S itself is chordal it is SIMPLE-tree-realizable.
      1. realize a non-simple tree by entropy-preserving surgery from a cyclic
         seed (hec.cycle_surgery), if a seed is given; certify its fine-graining
         (chordal refined tree, N' recorded, coarse-grain verified).
    Returns (cert | None, info). info carries the BOUNDED negative when no tree
    is found: status, the bound, strategies tried — NEVER an unbounded
    non-existence claim.

    NOTE (honest scope): the seed-independent enumeration of fine-grained PMIs
    is left incomplete here, mirroring arXiv:2512.18702 (which postpones the
    full fine-graining of correlation hypergraphs to future work). The
    correctness core — coarse_grain + the chordality certificate — is exact and
    round-trip validated; the realization SEARCH is bounded by the surgery
    backend and the cyclic seeds available.
    """
    from hec.chordality import simple_forest_realizable

    Sd = S_target if isinstance(S_target, dict) else vector_from_paper(S_target, n)
    base = simple_forest_realizable(Sd, n)
    if base["chordal"]:
        log(f"[{name}] base vector is CHORDAL — realizable by a SIMPLE tree.")
        from hec.tree_builder import build_simple_forest
        T = build_simple_forest(Sd, n)
        party = {v: v for v in T.nodes if not str(v).startswith("q")}
        cert = certify_fine_graining(T, party, Sd, n, name, out_dir, log)
        return cert, {"status": "tree", "n_prime": n, "route": "base_chordal"}

    strategies = []
    if cyclic_seed is not None:
        from hec.cycle_surgery import surgery
        G0, p0 = cyclic_seed
        path, sinfo = surgery(G0, p0, n, name, target=Sd, max_nodes=surgery_nodes,
                              out_dir=None if out_dir is None else out_dir,
                              log=lambda m: None)
        strategies.append({"surgery": sinfo["status"],
                           "best_cyclomatic": sinfo.get("best_cyclomatic"),
                           "nodes": sinfo.get("nodes")})
        if sinfo["status"] == "tree":
            # rebuild the found tree and certify its fine-graining
            import json
            cert = json.loads(path.read_text())

            def nrm(x):
                return int(x) if x in ("0", "1", "2", "3", "4", "5") else x
            T = nx.Graph()
            pm = {}
            for u, v, w in cert["edges"]:
                T.add_edge(nrm(u), nrm(v), capacity=w)
            for vk, lab in cert["party"].items():
                pm[nrm(vk)] = nrm(lab) if isinstance(lab, str) and lab.isdigit() else lab
            fc = certify_fine_graining(T, pm, Sd, n, name, out_dir, log)
            if fc is not None:
                return fc, {"status": "tree", "n_prime": fc["n_prime"],
                            "route": "surgery+finegraining_cert"}

    info = {
        "status": "no_tree_found",
        "bound_N_prime": n + bound,
        "strategies": strategies,
        "qualifier": (f"BOUNDED: no tree-able fine-graining found for s={name} "
                      f"up to the searched bound (surgery from the available "
                      f"cyclic seed; N' implicitly bounded by the surgery move "
                      f"set). This is NOT a proof that no tree realization "
                      f"exists, and NOT a statement about realizability ("
                      f"the ray is holographic). The complete seed-independent "
                      f"fine-graining enumeration is future work."),
    }
    log(f"[{name}] no tree-able fine-graining found under the searched bound. "
        f"BOUNDED — not a non-existence claim.")
    return None, info

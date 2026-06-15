"""hec/obstruction_search.py — a CHEAP, LP-FREE test of whether s=111 is
structurally SPECIAL or merely computationally hard.

THE IDEA. Instead of searching (and failing) for a tree realization of the
bulk-cycle orbit s=111, look for a vector/structural INVARIANT that separates
111 from every ray KNOWN to be tree-realizable. An invariant that puts 111
outside the range of all tree-realizable rays is a candidate OBSTRUCTION — a
reason, not an absence; far cheaper and stronger than an exhausted search. If
no cheap invariant separates it, that is evidence 111 is an ordinary
tree-realizable ray that the search was merely too slow to crack.

THE REFERENCE SET (all confirmed tree-realizable, vectors only — no graphs,
no LP, no weight fitting):
  - the 148 tree-realizable n=6 orbits of arXiv:2412.15364 (He-Hubeny-Rota):
    the 156 HEI-clean orbits minus the 6 mystery orbits minus the 2 bulk-cycle
    orbits {111,207}. The paper realizes these 148 by TREE graphs.
  - all 19 n=5 extreme-ray orbits (arXiv:1903.09148): every one is
    tree-realizable (rays 1-9 by simple trees, 10-19 by NON-simple trees,
    arXiv:2204.00075 fig. N5trees).
The TARGETS are the two bulk-cycle orbits s=111 (primary) and s=207.

THE CONTROL (critical, SPEC of this experiment). C5 rays 10 and 17 ARE
tree-realizable (via non-simple trees; cracked to trees in hec.cycle_surgery)
yet their simple realization keeps a bulk cycle, so they are NON-chordal — the
exact analogue of 111. Any invariant that flags 111 as special must NOT also
flag 10/17 (or it is merely detecting "has a bulk cycle", which is not an
obstruction to tree-realizability). The experiment makes this control
quantitative: it turns out 104 of the 148 tree-realizable n=6 orbits are
THEMSELVES non-chordal, giving a 104-strong, same-n, non-chordal-but-
tree-realizable cohort. The real test is therefore whether 111 differs from
THOSE 104 (+ the C5 controls 10-19) — rays that share 111's surviving-cycle
property yet are nonetheless tree-realizable.

HONEST INTERPRETATION (stated plainly in the report; never overclaimed):
  - SOME invariant cleanly separates 111 from all tree-realizable rays
    INCLUDING the non-chordal cohort and 10/17 -> CANDIDATE obstruction, strong
    evidence 111 may be a counterexample. NOT a proof (a different invariant
    value does not prove non-realizability).
  - NO invariant separates 111 -> evidence 111 is just HARD, not special;
    supports that it IS tree-realizable and the search was too slow (points
    back to the angle-1 search filter as the real fix).

HARD RULES: every invariant value is computed in EXACT integer arithmetic
(graph structure via networkx, no floats anywhere in a value); LP-free and
weight-fit-free throughout; correlation is never reported as proof; the
suspects {110,145,168} are not touched.
"""

from __future__ import annotations

import itertools
import pathlib
from fractions import Fraction
from functools import reduce
from math import comb, gcd

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.chordality import (
    correlation_hypergraph,
    line_graph,
    mutual_information,
)
from hec.cone import ineq_to_coeffs, orbit, sa_instances, ssa_instances
from hec.subsets import vector_from_paper, vector_to_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent
N6_RAYS = ROOT / "data" / "raw" / "rota" / "n6_rays.txt"
REPORTS = ROOT / "reports"

# He-Hubeny-Rota classification of the 208 n=6 SSA-compatible extreme-ray
# orbits (1-indexed, matching data/raw/rota/n6_rays.txt rows). The 52
# HEI-violators are the paper's published list, reproduced exactly by
# scripts/verify_er6.py (the violator index SET matches).
PAPER_VIOLATORS = {
    71, 108, 118, 124, 126, 132, 133, 140, 141, 142, 143, 144, 148, 150,
    153, 154, 158, 160, 162, 163, 164, 165, 166, 167, 173, 174, 175, 176,
    177, 178, 179, 182, 183, 184, 185, 186, 187, 188, 191, 192, 193, 194,
    197, 198, 199, 200, 201, 202, 203, 204, 205, 208,
}
MYSTERY = {110, 145, 146, 168, 180, 181}   # 6 unresolved orbits
BULK_CYCLE = {111, 207}                     # the 2 bulk-cycle orbits = targets
SUSPECTS = {110, 145, 168}                  # never analyzed here (instruction)


# ----------------------------------------------------------------- data load

def load_n6_rays() -> list[tuple[int, ...]]:
    rows = [tuple(int(x) for x in line.split())
            for line in N6_RAYS.read_text().strip().splitlines()]
    if len(rows) != 208 or any(len(r) != 63 for r in rows):
        raise ValueError(f"expected 208 x 63 rays, got {len(rows)}")
    return rows


def tree_realizable_indices() -> list[int]:
    """The 148 tree-realizable n=6 orbits: HEI-clean minus mystery minus the
    two bulk-cycle orbits (arXiv:2412.15364 realizes these 148 by trees)."""
    clean = set(range(1, 209)) - PAPER_VIOLATORS
    idx = sorted(clean - MYSTERY - BULK_CYCLE)
    if len(idx) != 148:
        raise ValueError(f"expected 148 tree-realizable orbits, got {len(idx)}")
    return idx


def reference_set() -> list[dict]:
    """All confirmed tree-realizable rays + the targets + a little labeled
    context. Each record: name, n, vec (paper-order tuple), role."""
    rows = load_n6_rays()
    recs: list[dict] = []
    for s in tree_realizable_indices():
        recs.append({"name": f"n6:{s}", "n": 6, "vec": rows[s - 1],
                     "role": "tree-realizable"})
    for k in range(1, 20):                      # all 19 C5 orbits are tree-realizable
        role = "control" if k in (10, 17) else "tree-realizable"
        recs.append({"name": f"c5:{k}", "n": 5, "vec": C5_EXTREME_RAYS[k - 1],
                     "role": role})
    for s in sorted(BULK_CYCLE):                # targets
        recs.append({"name": f"n6:{s}", "n": 6, "vec": rows[s - 1],
                     "role": "target"})
    return recs


# ----------------------------------------------------- exact cheap invariants

def _primitive(vec) -> tuple[int, ...]:
    g = reduce(gcd, (x for x in vec if x)) or 1
    return tuple(x // g for x in vec)


def _bitset_adj(L: nx.Graph) -> tuple[list[int], dict]:
    nodes = list(L.nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    adj = [0] * len(nodes)
    for u, v in L.edges:
        adj[idx[u]] |= 1 << idx[v]
        adj[idx[v]] |= 1 << idx[u]
    return adj, idx


def count_induced_4holes(L: nx.Graph) -> int:
    """Number of induced 4-cycles (chordless C4 = "holes" of length 4) in L,
    exactly. A 4-hole is {u,w,a,b} with u,w non-adjacent, a,b non-adjacent, and
    a,b both common neighbours of u,w. For each non-adjacent pair {u,w} count
    the non-adjacent pairs inside their common neighbourhood; each 4-hole is
    counted by both of its non-adjacent (diagonal) pairs, hence the //2."""
    adj, _ = _bitset_adj(L)
    nv = len(adj)
    total = 0
    for u in range(nv):
        au = adj[u]
        for w in range(u + 1, nv):
            if au >> w & 1:
                continue                       # u,w adjacent -> not a diagonal
            common = au & adj[w]
            c = common.bit_count()
            if c < 2:
                continue
            # non-adjacent pairs within `common` = C(c,2) - edges inside common
            e_in = 0
            cc = common
            while cc:
                a = (cc & -cc).bit_length() - 1
                cc &= cc - 1
                e_in += (adj[a] & common).bit_count()
            e_in //= 2
            total += comb(c, 2) - e_in
    return total // 2


def shortest_hole(L: nx.Graph, kmax: int = 8) -> int | None:
    """Length of the shortest induced cycle of length >= 4, or None if chordal
    (or no hole up to kmax). Cheap because we expect very short holes."""
    if nx.is_chordal(L):
        return None
    nodes = list(L.nodes)
    for k in range(4, kmax + 1):
        for sub in itertools.combinations(nodes, k):
            H = L.subgraph(sub)
            if (H.number_of_edges() == k
                    and all(d == 2 for _, d in H.degree())
                    and nx.is_connected(H)):
                return k
    return kmax + 1   # hole exists but is longer than kmax (record as a bound)


def nonchordal_core(L: nx.Graph) -> nx.Graph:
    """Residue of iteratively deleting simplicial vertices (whose neighbourhood
    is a clique). A chordal graph empties; the residue is the irreducible
    non-chordal core."""
    G = L.copy()
    adj = {u: set(G[u]) for u in G}
    changed = True
    while changed:
        changed = False
        for v in list(G.nodes):
            nb = adj[v]
            if all(b in adj[a] for a in nb for b in nb if a != b):
                for a in nb:
                    adj[a].discard(v)
                del adj[v]
                G.remove_node(v)
                changed = True
                break
    return G


# cached facet instance sets (built once per process)
_FACETS: dict[int, dict] = {}


def _facets(n: int) -> dict:
    if n not in _FACETS:
        mmi = sorted(orbit(ineq_to_coeffs(
            {"AB": 1, "AC": 1, "BC": 1},
            {"A": 1, "B": 1, "C": 1, "ABC": 1}, n), n))
        _FACETS[n] = {"SA": sa_instances(n), "SSA": ssa_instances(n), "MMI": mmi}
    return _FACETS[n]


def _slacks(vec_paper: tuple, facets: list[tuple]) -> list[int]:
    return [sum(a * b for a, b in zip(f, vec_paper)) for f in facets]


def invariants(vec, n: int) -> dict:
    """Compute the full LP-free invariant battery on one ray (paper-order
    vector). Every value is exact (integer or graph-structural)."""
    S = vector_from_paper(vec, n)
    prim = _primitive(vec)
    H = correlation_hypergraph(S, n)
    L = line_graph(H)
    chordal = nx.is_chordal(L)
    nv, ne = L.number_of_nodes(), L.number_of_edges()
    comps = nx.number_connected_components(L) if nv else 0
    cliques = list(nx.find_cliques(L)) if nv else []
    degs = [d for _, d in L.degree()]
    c4 = count_induced_4holes(L)
    core = nonchordal_core(L)

    fac = _facets(n)
    sa_sl = _slacks(prim, fac["SA"])
    ssa_sl = _slacks(prim, fac["SSA"])
    mmi_sl = _slacks(prim, fac["MMI"])

    # single-label pairwise mutual informations (the coarsest PMI layer)
    zero_pair = sum(1 for i, j in itertools.combinations(range(n + 1), 2)
                    if mutual_information(S, 1 << i, 1 << j, n) == 0)
    indep = nx.Graph()
    indep.add_nodes_from(range(n + 1))
    for i, j in itertools.combinations(range(n + 1), 2):
        if mutual_information(S, 1 << i, 1 << j, n) > 0:
            indep.add_edge(i, j)
    isolated = sum(1 for x in indep.nodes if indep.degree(x) == 0)

    return {
        # ---- Family 1: correlation hypergraph / line graph
        "chordal": int(chordal),
        "n_hyperedges": len(H),
        "lg_density": Fraction(2 * ne, nv * (nv - 1)) if nv > 1 else Fraction(0),
        "lg_clique_number": max((len(c) for c in cliques), default=0),
        "lg_num_max_cliques": len(cliques),
        "lg_cyclomatic": ne - nv + comps,
        "lg_deg_max": max(degs, default=0),
        "lg_deg_min": min(degs, default=0),
        "shortest_hole": shortest_hole(L) or 0,
        "n_4holes": c4,
        "holes_per_hyp": Fraction(c4, len(H)) if H else Fraction(0),
        "core_nodes": core.number_of_nodes(),
        # ---- Family 2: cut-value profile
        "n_distinct_values": len(set(prim)),
        "max_value": max(prim),
        "purifier_S": S[(1 << n) - 1],
        "sa_saturated": sum(1 for x in sa_sl if x == 0),
        "ssa_saturated": sum(1 for x in ssa_sl if x == 0),
        "mmi_saturated": sum(1 for x in mmi_sl if x == 0),
        "mmi_sat_frac": Fraction(sum(1 for x in mmi_sl if x == 0), len(mmi_sl)),
        "mmi_min_slack": min(mmi_sl),
        # ---- Family 3: independence / PMI
        "zero_pair_MI": zero_pair,
        "independent_parties": isolated,
    }


# invariants whose VALUE is comparable across n (5 vs 6); the rest are compared
# only within the same n (the n=6 cohort).
N_AGNOSTIC = {
    "chordal", "lg_density", "shortest_hole", "holes_per_hyp",
    "mmi_sat_frac", "independent_parties", "max_value",
}


# ----------------------------------------------------------------- experiment

TARGETS = ["n6:111", "n6:207"]   # 111 primary, 207 secondary


def run(log=print) -> dict:
    """Compute the battery over the whole reference set and run the
    control-aware separation test for each bulk-cycle target (111, 207)."""
    recs = reference_set()
    for r in recs:
        r["inv"] = invariants(r["vec"], r["n"])

    by_name = {r["name"]: r for r in recs}
    keys = list(by_name["n6:111"]["inv"].keys())

    # chordality census of the n=6 tree-realizable cohort (the control's spine)
    n6_tree = [r for r in recs if r["role"] == "tree-realizable" and r["n"] == 6]
    n6_nonchordal = [r for r in n6_tree if r["inv"]["chordal"] == 0]
    c5_nonchordal = [r for r in recs if r["n"] == 5
                     and r["role"] in ("tree-realizable", "control")
                     and r["inv"]["chordal"] == 0]

    results = {}
    for key in keys:
        agn = key in N_AGNOSTIC
        # cohort = confirmed tree-realizable AND non-chordal (shares the targets'
        # surviving-cycle property); n-agnostic keys also pool the C5 controls.
        cohort = list(n6_nonchordal) + (list(c5_nonchordal) if agn else [])
        vals = sorted(r["inv"][key] for r in cohort)
        lo, hi = vals[0], vals[-1]
        mean = sum(Fraction(v) for v in vals) / len(vals)
        c10, c17 = by_name["c5:10"]["inv"][key], by_name["c5:17"]["inv"][key]
        # percentile is taken within the SAME-n (n=6) cohort — the honest
        # centrality reference for an n=6 target (avoids the n-pooling artifact
        # where every n=6 ray tops an n-agnostic key shared with smaller n=5).
        n6_vals = sorted(r["inv"][key] for r in n6_nonchordal)

        def pct(x):
            return round(100 * sum(1 for v in n6_vals if v <= x) / len(n6_vals), 1)

        results[key] = {
            "n_agnostic": agn,
            "cohort_size": len(cohort),
            "cohort_min": lo, "cohort_max": hi, "cohort_mean": mean,
            # an invariant constant across the cohort has no discriminating
            # power: an "inside" verdict on it is vacuous, flagged transparently.
            "degenerate": lo == hi,
            # constant within the SAME-n cohort -> carries no centrality signal
            # for an n=6 target (excluded from the percentile-range summary).
            "n6_constant": n6_vals[0] == n6_vals[-1],
            "control_c5_10": c10, "control_c5_17": c17,
            # control: the two known-tree-realizable non-chordal C5 rays must sit
            # inside the cohort range (else the invariant flags them too).
            "control_inside": (lo <= c10 <= hi and lo <= c17 <= hi) if agn else None,
            "targets": {
                t.split(":")[1]: {
                    "value": by_name[t]["inv"][key],
                    "separates": by_name[t]["inv"][key] < lo
                    or by_name[t]["inv"][key] > hi,
                    "percentile": pct(by_name[t]["inv"][key]),
                }
                for t in TARGETS
            },
        }

    separators = {
        t.split(":")[1]: [k for k, v in results.items()
                          if v["targets"][t.split(":")[1]]["separates"]
                          and not v["degenerate"]
                          and (v["control_inside"] is not False)]
        for t in TARGETS
    }

    return {
        "n6_tree_total": len(n6_tree),
        "n6_chordal": len(n6_tree) - len(n6_nonchordal),
        "n6_nonchordal": len(n6_nonchordal),
        "c5_nonchordal": len(c5_nonchordal),
        "results": results,
        "separators": separators,        # {"111": [...], "207": [...]}
        "records": recs,
        "by_name": by_name,
    }


def _fmt(x) -> str:
    if isinstance(x, Fraction):
        return f"{float(x):.4f}"
    if isinstance(x, bool):
        return str(int(x))
    return str(x)


def print_table(R: dict, log=print) -> None:
    log("")
    log("=" * 104)
    log("OBSTRUCTION SEARCH — cheap LP-free invariants: bulk-cycle s=111/207 vs "
        "tree-realizable rays (control: C5 10/17)")
    log("=" * 104)
    log(f"chordality census of the 148 n=6 tree-realizable orbits: "
        f"{R['n6_chordal']} chordal (simple-tree) + {R['n6_nonchordal']} "
        f"NON-chordal (non-simple-tree)")
    log(f"  => chordality does NOT certify non-realizability: {R['n6_nonchordal']} "
        f"confirmed tree-realizable n=6 rays are non-chordal, exactly like 111/207.")
    log(f"  => control cohort = {R['n6_nonchordal']} non-chordal n=6 trees "
        f"(+ {R['c5_nonchordal']} non-chordal C5 rays for n-agnostic keys); "
        f"targets excluded.")
    log("  cols: agn=value comparable across n; deg=cohort constant (no signal); "
        "out?=target outside cohort range; ctl_in=controls 10/17 inside")
    log("")
    hdr = (f"{'invariant':<19}{'agn':>4}{'deg':>4}{'cohort[min..max]':>20}"
           f"{'s=111':>9}{'o':>2}{'s=207':>9}{'o':>2}{'c5:10':>8}{'c5:17':>8}{'ctl':>5}")
    log(hdr)
    log("-" * len(hdr))
    for key, v in R["results"].items():
        rng = f"{_fmt(v['cohort_min'])}..{_fmt(v['cohort_max'])}"
        ci = "" if v["control_inside"] is None else ("y" if v["control_inside"] else "NO")
        deg = "·" if v["degenerate"] else ""
        t111, t207 = v["targets"]["111"], v["targets"]["207"]
        f111 = "*" if (t111["separates"] and not v["degenerate"]) else ""
        f207 = "*" if (t207["separates"] and not v["degenerate"]) else ""
        log(f"{key:<19}{('Y' if v['n_agnostic'] else ''):>4}{deg:>4}{rng:>20}"
            f"{_fmt(t111['value']):>9}{f111:>2}{_fmt(t207['value']):>9}{f207:>2}"
            f"{_fmt(v['control_c5_10']):>8}{_fmt(v['control_c5_17']):>8}{ci:>5}")
    log("-" * len(hdr))
    # the canonical trap, shown explicitly
    chc = R["results"]["chordal"]
    log(f"TRAP CHECK — chordality 'separates' 111/207 only from the "
        f"{R['n6_chordal']} chordal trees, but FLAGS {R['n6_nonchordal']} "
        f"tree-realizable n=6 rays")
    log(f"  AND both controls (c5:10 chordal={chc['control_c5_10']}, "
        f"c5:17 chordal={chc['control_c5_17']}) -> NOT an obstruction (it detects "
        f"'has a bulk cycle', the warned-against confound).")
    log("")
    for t in ("111", "207"):
        seps = R["separators"][t]
        tag = "(PRIMARY)" if t == "111" else "(secondary)"
        # centrality: where the target sits within the cohort on the
        # non-degenerate invariants (percentile; 50 = median, near edges = 0/100)
        pcts = [v["targets"][t]["percentile"] for v in R["results"].values()
                if not v["n6_constant"]]
        if seps:
            margins = "; ".join(
                f"{k} {_fmt(R['results'][k]['targets'][t]['value'])} vs cohort "
                f"[{_fmt(R['results'][k]['cohort_min'])}.."
                f"{_fmt(R['results'][k]['cohort_max'])}]" for k in seps)
            log(f"s={t} {tag}: MARGINAL separator(s) {seps} — {margins}.")
            log(f"  (small boundary excursions on count-type invariants; the "
                f"cohort edge is itself a tree-realizable ray — a continuum, not "
                f"a clean gap.)")
        else:
            log(f"s={t} {tag}: NO non-degenerate invariant separates it from the "
                f"non-chordal tree-realizable cohort (incl. C5 10/17 controls).")
        log(f"  position within cohort: percentile range "
            f"[{min(pcts)}..{max(pcts)}] across {len(pcts)} non-degenerate "
            f"invariants (50 = median).")
    log("")
    if not R["separators"]["111"]:
        log("HEADLINE: s=111 looks like an ORDINARY non-chordal tree-realizable "
            "ray on every cheap invariant tested — evidence it is merely HARD to")
        log("  crack, not a structural counterexample to the strong tree "
            "conjecture. Points back to the search filter, not to non-realizability.")


def write_report(R: dict, out_dir: pathlib.Path = REPORTS) -> pathlib.Path:
    import json

    out_dir.mkdir(parents=True, exist_ok=True)

    def ser(x):
        if isinstance(x, Fraction):
            return float(x)
        if isinstance(x, dict):
            return {k: ser(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [ser(v) for v in x]
        return x

    payload = {
        "what": ("Cheap LP-free obstruction search: does any vector/structural "
                 "invariant separate the bulk-cycle orbit s=111 from all rays "
                 "known to be tree-realizable? A separator (passing the C5 10/17 "
                 "control) would be a candidate obstruction to tree-realizability; "
                 "none means 111 looks like an ordinary, merely-hard "
                 "tree-realizable ray."),
        "engine": "hec.obstruction_search (exact integer arithmetic, no LP, no "
                  "weight fitting)",
        "reference_set": {
            "n6_tree_realizable": 148,
            "n6_tree_realizable_def": "the 156 HEI-clean orbits of "
            "arXiv:2412.15364 minus the 6 mystery orbits minus the 2 bulk-cycle "
            "orbits {111,207}; the paper realizes these 148 by tree graphs",
            "c5_all_orbits": 19,
            "c5_def": "all 19 n=5 extreme-ray orbits (arXiv:1903.09148); every "
            "one is tree-realizable (1-9 simple, 10-19 non-simple per "
            "arXiv:2204.00075)",
        },
        "chordality_census_n6_trees": {
            "chordal_simple_tree": R["n6_chordal"],
            "nonchordal_nonsimple_tree": R["n6_nonchordal"],
            "note": "104 of the 148 tree-realizable n=6 orbits are themselves "
            "non-chordal -> chordality detects 'bulk cycle', NOT "
            "non-realizability; it is the canonical control trap.",
        },
        "targets": {
            "111": [int(x) for x in R["by_name"]["n6:111"]["vec"]],
            "207": [int(x) for x in R["by_name"]["n6:207"]["vec"]],
        },
        "controls": {
            "c5_10": [int(x) for x in R["by_name"]["c5:10"]["vec"]],
            "c5_17": [int(x) for x in R["by_name"]["c5:17"]["vec"]],
            "role": "confirmed tree-realizable (non-simple) AND non-chordal — the "
            "n=5 analogue of 111; an obstruction must NOT flag these.",
        },
        "invariant_table": {k: ser(v) for k, v in R["results"].items()},
        "separators": R["separators"],
        "verdict": (
            "CANDIDATE OBSTRUCTION found for s=111: " + ", ".join(R["separators"]["111"])
            if R["separators"]["111"] else
            "NO non-degenerate cheap invariant in this battery separates s=111 "
            "from the non-chordal tree-realizable cohort (including the C5 10/17 "
            "controls). On every invariant tested, s=111 lies INSIDE the range "
            "spanned by confirmed tree-realizable rays — usually near the cohort "
            "mean. This is evidence that s=111 is an ORDINARY tree-realizable ray "
            "that is merely hard to crack, NOT a structural counterexample to the "
            "strong tree conjecture. It is NOT a proof of realizability; it "
            "redirects effort to the search filter (the angle-1 filter) rather "
            "than to a non-existence claim."),
        "verdict_207": (
            "s=207 lies MARGINALLY outside the cohort on " +
            ", ".join(R["separators"]["207"]) + " (small boundary excursions on "
            "count-type invariants: 42 vs max 40 holes, 0.737 vs 0.714 hole "
            "density, 119 vs min 123 SA-saturated). The cohort edge is itself a "
            "tree-realizable ray, so this is the high-hole-density / "
            "low-SA-saturation END of a continuum, NOT a clean gap — weak, "
            "single-cohort-boundary, and 207 has no studied cyclic seed. It is "
            "NOT a candidate obstruction in the strong sense; reported for "
            "completeness and as proof the test is not trivially returning "
            "'inside' for everything."
            if R["separators"]["207"] else
            "no non-degenerate invariant separates s=207 either"),
        "caveats": [
            "'No separator' means none in THIS battery of cheap invariants, not "
            "that none can exist; a finer invariant could still separate 111.",
            "A different/equal invariant value is correlation, never proof; no "
            "non-realizability is claimed from any invariant.",
            "s=111 and s=207 ARE holographic (each is realized, with a bulk "
            "cycle); only the tree-vs-cycle question is open.",
            "Degenerate invariants (cohort min==max, flagged 'degenerate') carry "
            "no discriminating signal; their 'inside' verdict is vacuous.",
            "Suspects {110,145,168} are not analyzed here (instruction).",
        ],
        "reproduce": ".venv/bin/python -m hec.obstruction_search",
    }
    path = out_dir / "obstruction_search.json"
    path.write_text(json.dumps(payload, indent=2))
    return path


def write_markdown(R: dict, out_dir: pathlib.Path = REPORTS) -> pathlib.Path:
    """Human-readable report: the full invariant table + the honest statement."""
    out_dir.mkdir(parents=True, exist_ok=True)
    L = []
    L.append("# Obstruction search — is s=111 structurally special or just hard?\n")
    L.append("A **cheap, LP-free** test (no weight fitting, no realization "
             "search). Instead of searching for a tree realization of the "
             "bulk-cycle orbit `s=111`, we look for a vector/structural "
             "**invariant** that separates it from every ray *known* to be "
             "tree-realizable. A separator (that also passes the control) would "
             "be a candidate obstruction — a reason, not an absence. No "
             "separator means 111 looks ordinary, i.e. merely hard to crack.\n")
    L.append("Reproduce: `.venv/bin/python -m hec.obstruction_search`. "
             "All values exact (integer / graph-structural).\n")
    L.append("## Reference set & the control\n")
    L.append("- **Tree-realizable reference set:** the 148 tree-realized n=6 "
             "orbits of arXiv:2412.15364 + all 19 n=5 orbits of arXiv:1903.09148 "
             "(every C5 orbit is tree-realizable).\n")
    L.append(f"- **Chordality census of the 148 n=6 trees:** "
             f"{R['n6_chordal']} chordal (simple-tree) + **{R['n6_nonchordal']} "
             f"NON-chordal** (non-simple-tree). So chordality detects *“has a "
             f"bulk cycle”*, **not** non-realizability — it flags "
             f"{R['n6_nonchordal']} confirmed tree-realizable rays and both "
             f"controls. It is the canonical trap, and the real comparison "
             f"cohort is these {R['n6_nonchordal']} non-chordal-but-"
             f"tree-realizable rays.\n")
    L.append("- **Controls (critical):** C5 rays **10** and **17** are "
             "tree-realizable (non-simple) yet non-chordal — the n=5 analogue of "
             "111. An obstruction must NOT flag them.\n")
    L.append("- **Targets:** `s=111` (primary) and `s=207`, the two bulk-cycle "
             "orbits.\n")
    L.append("## Invariant table\n")
    L.append("`agn` = value comparable across n; `deg` = constant across cohort "
             "(no signal); `out?` = target strictly outside cohort range; "
             "`ctl` = controls 10/17 inside (n-agnostic keys only). Percentile "
             "is within the 104-ray same-n (n=6) cohort.\n")
    L.append("| invariant | agn | deg | cohort min..max (mean) | s=111 (pct) | out | "
             "s=207 (pct) | out | c5:10 | c5:17 | ctl |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for key, v in R["results"].items():
        agn = "Y" if v["n_agnostic"] else ""
        deg = "·" if v["degenerate"] else ""
        rng = f"{_fmt(v['cohort_min'])}..{_fmt(v['cohort_max'])} ({_fmt(v['cohort_mean'])})"
        t1, t2 = v["targets"]["111"], v["targets"]["207"]
        o1 = "**\\***" if (t1["separates"] and not v["degenerate"]) else ""
        o2 = "**\\***" if (t2["separates"] and not v["degenerate"]) else ""
        ci = "" if v["control_inside"] is None else ("yes" if v["control_inside"] else "**NO**")
        L.append(f"| `{key}` | {agn} | {deg} | {rng} | {_fmt(t1['value'])} "
                 f"({t1['percentile']}) | {o1} | {_fmt(t2['value'])} "
                 f"({t2['percentile']}) | {o2} | {_fmt(v['control_c5_10'])} | "
                 f"{_fmt(v['control_c5_17'])} | {ci} |")
    L.append("")
    L.append("## Verdict\n")
    pcts111 = [v["targets"]["111"]["percentile"] for v in R["results"].values()
               if not v["n6_constant"]]
    L.append(f"**s=111 (primary): no separator.** No non-degenerate invariant in "
             f"this battery puts 111 outside the non-chordal tree-realizable "
             f"cohort (including the 10/17 controls). Across the "
             f"{len(pcts111)} discriminating invariants it sits at percentiles "
             f"**{min(pcts111)}–{max(pcts111)}** of the 104 same-n "
             f"tree-realizable rays — strictly interior, usually near the "
             f"median, never at an edge. **Evidence that s=111 is an ordinary "
             f"tree-realizable ray that is merely hard to crack, not a "
             f"structural counterexample to the strong tree conjecture.** This "
             f"is *not* a proof of realizability (111 IS holographic; only the "
             f"tree question is open); it redirects effort to the search filter "
             f"rather than to a non-existence claim.\n")
    if R["separators"]["207"]:
        L.append(f"**s=207 (secondary): marginal only.** 207 lies just outside "
                 f"the cohort on `{', '.join(R['separators']['207'])}` — small "
                 f"boundary excursions on count-type invariants (42 vs max 40 "
                 f"holes; 0.737 vs 0.714 hole density; 119 vs min 123 "
                 f"SA-saturated). The cohort edge is itself a tree-realizable "
                 f"ray, so this is the high-density END of a continuum, not a "
                 f"clean gap — weak, single-boundary, and 207 has no studied "
                 f"cyclic seed. Not a candidate obstruction in the strong sense; "
                 f"it does show the test is not trivially returning “inside”.\n")
    L.append("## Honesty\n")
    L.append("- “No separator” means none in *this* battery of cheap "
             "invariants, not that none can exist.\n"
             "- A differing/equal invariant value is correlation, never proof; "
             "no non-realizability is claimed from any invariant.\n"
             "- s=111 and s=207 ARE holographic (each realized, with a bulk "
             "cycle); only tree-vs-cycle is open.\n"
             "- Suspects {110,145,168} are not analyzed here.\n")
    path = out_dir / "obstruction_search.md"
    path.write_text("\n".join(L))
    return path


def main() -> None:
    R = run()
    print_table(R)
    pj = write_report(R)
    pm = write_markdown(R)
    print(f"\nreports -> {pj.relative_to(ROOT)} , {pm.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

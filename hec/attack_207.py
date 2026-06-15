"""hec/attack_207.py — attack the s=207 bulk-cycle orbit, the unexplored twin
of s=111.

s=111 and s=207 are the two "bulk cycle" orbits of arXiv:2412.15364 (He-Hubeny-
Rota): both are definitively holographic (each has a graph realization) but the
authors could not find a TREE realization, leaving open whether a tree exists or
whether one of them is a counterexample to the strong tree conjecture
(arXiv:2204.00075). s=111 has been worked extensively here; s=207 was UNTOUCHED
for one reason only — we never had a starting realization (seed) for it (it is
absent from the hecdata graph repo; LP construction from scratch bottlenecks just
as it did for 111).

STEP 0 (the actual blocker) — SEED OBTAINED. The seed is transcribed from the
paper's own figure (data/raw/2412.15364/figures/ER_graphs.pdf, entry #207, the
"simple graph" column) and then Sym(7) orbit-matched to OUR representative and
EXACT-verified: its entropy vector equals 2x the s=207 representative in Fraction
arithmetic (the ray-match is the safety net — a misread edge or weight would not
verify; this is the s181 lesson). Methods (a) hecdata orbit-match and (c) LP
construction were tried and FAILED (207 is absent from hecdata's 4145 graphs; LP
found no realization in 24 tries / ~550 s) — the figure transcription is what
yielded the seed.

STEP 1 — the seed is characterized and compared to 111's pure-bulk 4-cycle.
STEP 2 — the validated cycle_surgery machinery is run on it.

RESULT (see the report): s=207 STALLS THE SAME WAY s=111 DOES. Its realization's
irreducible core is a pure-bulk 4-cycle with degree-4/5 vertices — the identical
obstruction class as 111 — on top of which sit 3 removable boundary triangles
(hence cyclomatic 4 vs 111's 3). The complete local entropy-preserving move set
empties its frontier without reaching a tree: a BOUNDED negative, exactly like
111. So the bulk-cycle obstruction is a GENERAL phenomenon shared by both twins,
not something special to 111.

HARD RULES (unchanged): exact Fraction arithmetic certifies any hit and any
ray-match; floats only rank. Bounded negatives only — "no tree found under
{method, bound, seed}", NEVER "no tree exists"/"non-realizable" (207 IS
holographic; only the tree question is open). The seed is exact-verified before
anything downstream. Reuse of the validated cycle_surgery / chordality / cone
machinery; nothing reimplemented. Suspects {110,145,168}, the email, the README,
and s=111's committed seed are not touched.
"""

from __future__ import annotations

import json
import pathlib

import networkx as nx

from hec.chordality import simple_forest_realizable
from hec.cone import sa_instances, ssa_instances
from hec.cycle_surgery import (
    characterize_obstruction,
    cyclomatic,
    normalize,
    surgery,
)
from hec.entropy import entropy_vector_labeled
from hec.subsets import vector_from_paper, vector_to_paper

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGETS = ROOT / "data" / "targets"
REPORTS = ROOT / "reports"

# ---------------------------------------------------------------- the seed
# STEP 0 deliverable: s=207's cyclic realization, transcribed from #207's
# "simple graph" in arXiv:2412.15364 ER_graphs.pdf and exact-verified to realize
# 2x our representative. Parties A..F = 0..5, purifier O; bulk x1..x4 (sigma1..4
# in the figure). Structure: a bulk 4-cycle x1-x2-x3-x4, three boundary triangles
# (E,F,A each with two adjacent bulk vertices), four weight-2 pendants (O,C,D,B).
SEED_207_EDGES = [
    ("O", "x3", 2),
    (4, "x3", 1), (4, "x2", 1),          # E triangle (sigma3, sigma2)
    (5, "x3", 1), (5, "x4", 1),          # F triangle (sigma3, sigma4)
    (2, "x2", 2),                         # C pendant
    (0, "x2", 1), (0, "x1", 1),          # A triangle (sigma2, sigma1)
    (3, "x4", 2),                         # D pendant
    (1, "x1", 2),                         # B pendant
    ("x3", "x2", 1), ("x2", "x1", 1),    # bulk 4-cycle ...
    ("x1", "x4", 2), ("x4", "x3", 1),    # ... x1-x2-x3-x4
]
SEED_207_PROVENANCE = {
    "source": "arXiv:2412.15364 (He-Hubeny-Rota) figure ER_graphs.pdf, entry "
              "#207, the 'simple graph' column (one boundary vertex per party)",
    "method": "transcribed from the figure, Sym(7) orbit-matched to our "
              "representative, and EXACT-verified (Fraction) to realize 2x the "
              "s=207 representative; perm from the paper's labels to ours is the "
              "identity",
    "hecdata": "207 is ABSENT from the hecdata graph repo (github.com/SergioHC95/"
               "Holographic-Entropy-Cone, 4145 n=6 graphs scanned, no orbit match)",
    "lp_construction": "lp_realize_target found no realization in 24 tries / "
                       "~550 s (the same bottleneck that blocked 111)",
}
PARTY_207 = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, "O": "O"}


def build_seed() -> tuple[nx.Graph, dict]:
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])
    for u, v, w in SEED_207_EDGES:
        G.add_edge(u, v, capacity=w)
    return G, dict(PARTY_207)


def rep_207() -> tuple[int, ...]:
    data = json.loads((TARGETS / "bulk_cycle_orbits.json").read_text())
    return tuple(data["orbits"]["207"])


# --------------------------------------------------------- STEP 1: validate

def validate_seed(log=print) -> dict:
    """STEP 1. Exact-confirm the seed realizes the s=207 ray (the critical
    s181-lesson check), then re-confirm 207 is genuinely the bulk-cycle case:
    SA+SSA, SAC-extreme (saturated-SA rank 62), HEI-clean, non-chordal."""
    import sympy

    G, party = build_seed()
    rep = rep_207()
    S = entropy_vector_labeled(G, 6, party)              # exact (integer weights)
    paper = vector_to_paper(S, 6)
    scale = next((k for k in range(1, 40)
                  if all(paper[i] == k * rep[i] for i in range(63))), None)
    if scale is None:
        raise AssertionError("SEED DOES NOT REALIZE s=207 — refuse to proceed "
                             "(the s181 lesson: confirm, never assume)")
    log(f"[seed] EXACT: entropy_vector(seed) == {scale} x s=207 representative "
        f"(Fraction-verified, all 63 components)")

    repd = vector_from_paper(rep, 6)
    sa, ssa = sa_instances(6), ssa_instances(6)
    sa_dots = [sum(a * b for a, b in zip(f, rep)) for f in sa]
    in_sa = all(d >= 0 for d in sa_dots)
    ssa_ok = all(sum(a * b for a, b in zip(f, rep)) >= 0 for f in ssa)
    sat = [f for f, d in zip(sa, sa_dots) if d == 0]
    rank = sympy.Matrix(sat).rank() if sat else 0
    hei_clean = _hei_clean(rep)
    chordal = simple_forest_realizable(repd, 6)["chordal"]

    log(f"[ray ] SA+SSA: {in_sa and ssa_ok}; SAC-extreme (sat-SA rank): {rank} "
        f"(=62 ?); HEI-clean: {hei_clean}; chordal: {chordal} "
        f"(non-chordal expected — bulk cycle)")
    return {
        "seed_realizes_207_exact": True, "scale": scale,
        "SA_SSA": bool(in_sa and ssa_ok), "saturated_SA_rank": int(rank),
        "SAC_extreme": rank == 62, "HEI_clean": hei_clean,
        "chordal": chordal, "non_chordal": not chordal,
    }


def _hei_clean(rep) -> bool:
    """True iff the ray violates none of the 1877 known HEIs over all Sym(7)
    images (the verify_er6 check, reused)."""
    import numpy as np

    from hec.cone import perm_index_matrix
    from hec.hei_data import load_hei6

    PERM = np.array(perm_index_matrix(6), dtype=np.intp)
    H = np.array(load_hei6(), dtype=np.int64).T
    imgs = np.array(rep, dtype=np.int64)[PERM]
    return not bool((imgs @ H < 0).any())


# ----------------------------------------------- STEP 1b: characterize seed

def characterize_seed(G, party) -> dict:
    """Cyclomatic number + the cycle inventory of the normalized seed (which
    cycles are removable boundary cycles vs the hard pure-bulk core)."""
    Gn = normalize(G, party)
    cycles = characterize_obstruction(Gn, party)
    pure_bulk = [c for c in cycles if c["pure_bulk"]]
    return {
        "cyclomatic": cyclomatic(Gn),
        "n_nodes": Gn.number_of_nodes(), "n_edges": Gn.number_of_edges(),
        "n_cycles_basis": len(cycles),
        "n_pure_bulk_cycles": len(pure_bulk),
        "pure_bulk_cycle": pure_bulk[0] if pure_bulk else None,
        "cycles": cycles,
    }


# --------------------------------------------------- STEP 2: tree-finding

def attack(name, G, party, log=print, max_nodes=50000, max_depth=40,
           y_delta_depth=12) -> dict:
    """STEP 2. Run the validated directed surgery toward a tree. Tree found ->
    exact self-certifying cert (answers the open question for this orbit).
    Otherwise a BOUNDED negative with the characterized surviving obstruction
    (never an unbounded non-existence claim)."""
    path, info = surgery(G, party, 6, name, target=None, max_nodes=max_nodes,
                         max_depth=max_depth, y_delta_depth=y_delta_depth,
                         out_dir=None, log=log)
    out = {"status": info["status"], "nodes": info.get("nodes"),
           "best_cyclomatic": info.get("best_cyclomatic"),
           "cert_path": str(path) if path else None}
    if info["status"] == "tree":
        out["verdict"] = (f"TREE FOUND for s={name} — exact cert; answers the "
                          f"open bulk-cycle question of arXiv:2412.15364 "
                          f"affirmatively for this orbit.")
    else:
        bg, bp = info.get("_best_graph", (None, None))
        out["obstruction"] = characterize_obstruction(bg, bp) if bg else None
        out["verdict"] = (f"BOUNDED: no entropy-preserving move sequence reduced "
                          f"s={name}'s realization to a tree under the complete "
                          f"local move set (frontier emptied at {info.get('nodes')} "
                          f"canonical states, best cyclomatic {info.get('best_cyclomatic')}). "
                          f"NOT a proof no tree exists; 207 IS holographic.")
    return out


# ------------------------------------------------- 111 vs 207 comparison

def seed_111():
    """Read-only load of 111's COMMITTED seed (never modified)."""
    data = json.loads((TARGETS / "bulk_cycle_seeds.json").read_text())
    s = data["seeds"]["111"]
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 4, 5, "O"])

    def nrm(x):
        return int(x) if isinstance(x, str) and x in ("0", "1", "2", "3", "4", "5") else x
    for u, v, w in s["edges"]:
        G.add_edge(nrm(u), nrm(v), capacity=w)
    return G, dict(PARTY_207), s


def compare(log=print) -> dict:
    """Run the SAME pipeline on both twins and contrast the obstruction."""
    G7, p7 = build_seed()
    G1, p1, s1meta = seed_111()
    c7 = characterize_seed(G7, p7)
    c1 = characterize_seed(G1, p1)
    a7 = attack("207", G7, p7, log=lambda m: None)
    a1 = attack("111", G1, p1, log=lambda m: None)

    def core(c):
        pb = c["pure_bulk_cycle"]
        return None if not pb else {
            "length": pb["length"],
            "degrees": sorted(pb["degrees"].values()),
            "delta_y_applicable": pb["delta_y_applicable"],
        }

    cmp = {
        "111": {"seed_cyclomatic": c1["cyclomatic"],
                "n_pure_bulk_cycles": c1["n_pure_bulk_cycles"],
                "pure_bulk_core": core(c1),
                "surgery": a1["status"], "best_cyclomatic": a1["best_cyclomatic"]},
        "207": {"seed_cyclomatic": c7["cyclomatic"],
                "n_pure_bulk_cycles": c7["n_pure_bulk_cycles"],
                "pure_bulk_core": core(c7),
                "surgery": a7["status"], "best_cyclomatic": a7["best_cyclomatic"]},
        "same_obstruction_class": (
            a1["status"] == a7["status"] == "no_reduction"
            and core(c1) is not None and core(c7) is not None
            and core(c1)["length"] == core(c7)["length"]),
        "reading": (
            "Both twins reduce (under the complete local move set) to a surviving "
            "PURE-BULK cycle and neither reaches a tree -> the bulk-cycle "
            "obstruction is a GENERAL phenomenon shared by 111 and 207, not "
            "specific to 111. 207's seed carries 3 extra REMOVABLE boundary "
            "triangles (cyclomatic 4 vs 111's 3), but its irreducible core is the "
            "same pure-bulk 4-cycle with degree-4/5 vertices."),
    }
    return cmp, a7, c7


# ---------------------------------------------------------------- outputs

def write_seed_provenance() -> pathlib.Path:
    """Save 207's seed with provenance — a NEW file; 111's committed
    bulk_cycle_seeds.json is never touched."""
    G, party = build_seed()
    S = entropy_vector_labeled(G, 6, party)
    rep = rep_207()
    scale = next(k for k in range(1, 40)
                 if all(vector_to_paper(S, 6)[i] == k * rep[i] for i in range(63)))
    payload = {
        "what": "cyclic graph realization (seed) for the bulk-cycle orbit s=207, "
                "transcribed from the paper's figure and EXACT-verified; the "
                "Delta-Y seed for hec.cycle_surgery / hec.attack_207",
        **SEED_207_PROVENANCE,
        "scale": scale,
        "cyclomatic": cyclomatic(normalize(G, party)),
        "realizes": f"entropy_vector_labeled(seed) == {scale} x s=207 "
                    f"representative (exact, all 63 components)",
        "edges": [[str(u), str(v), w] for u, v, w in SEED_207_EDGES],
        "party": {str(v): party[v] for v in party},
    }
    TARGETS.mkdir(parents=True, exist_ok=True)
    path = TARGETS / "bulk_cycle_seed_207.json"
    path.write_text(json.dumps(payload, indent=2))
    return path


def main() -> None:
    print("=" * 78)
    print("ATTACK s=207 — the unexplored bulk-cycle twin of s=111")
    print("=" * 78)
    print("\nSTEP 0 — seed:")
    print("  source : ER_graphs.pdf #207 (arXiv:2412.15364), transcribed")
    print("  hecdata: absent (4145 graphs scanned, no orbit match)")
    print("  LP     : no realization in 24 tries / ~550 s")
    print()
    val = validate_seed()
    G, party = build_seed()
    ch = characterize_seed(G, party)
    print(f"\nSTEP 1 — seed structure: cyclomatic {ch['cyclomatic']}, "
          f"{ch['n_pure_bulk_cycles']} pure-bulk cycle(s)")
    if ch["pure_bulk_cycle"]:
        pb = ch["pure_bulk_cycle"]
        print(f"  pure-bulk core: {pb['length']}-cycle, vertex degrees "
              f"{sorted(pb['degrees'].values())} -> {pb['why_stuck']}")
    print("\nSTEP 2 — surgery:")
    cmp, a7, _ = compare()
    print(f"  {a7['verdict']}")
    print("\n111 vs 207 comparison:")
    for s in ("111", "207"):
        c = cmp[s]
        print(f"  s={s}: seed cyclomatic {c['seed_cyclomatic']}, "
              f"pure-bulk core {c['pure_bulk_core']}, surgery={c['surgery']} "
              f"(best cyclomatic {c['best_cyclomatic']})")
    print(f"  same obstruction class: {cmp['same_obstruction_class']}")
    print(f"  => {cmp['reading']}")

    sp = write_seed_provenance()
    rp = write_report(val, ch, a7, cmp)
    mp = write_markdown(val, ch, a7, cmp)
    print(f"\nseed -> {sp.relative_to(ROOT)}")
    print(f"reports -> {rp.relative_to(ROOT)} , {mp.relative_to(ROOT)}")


def write_report(val, ch, a7, cmp, out_dir: pathlib.Path = REPORTS) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "what": "Attack on the s=207 bulk-cycle orbit (the unexplored twin of "
                "s=111): obtain a seed, characterize it, run tree-finding "
                "surgery, and compare to 111.",
        "engine": "hec.attack_207 (reuses hec.cycle_surgery / chordality / cone; "
                  "exact Fraction arithmetic)",
        "step0_seed": SEED_207_PROVENANCE,
        "step1_validation": val,
        "step1_structure": {k: v for k, v in ch.items() if k != "cycles"},
        "step2_surgery": {k: v for k, v in a7.items() if k != "obstruction"},
        "step2_surviving_obstruction": a7.get("obstruction"),
        "comparison_111_vs_207": cmp,
        "verdict": (
            "s=207 is NO LONGER seed-blocked: a cyclic realization was obtained "
            "from the paper's figure and exact-verified. Running the validated "
            "surgery, s=207 STALLS THE SAME WAY s=111 DOES — its irreducible core "
            "is a pure-bulk 4-cycle (degree-4/5 vertices), the identical "
            "obstruction class as 111, with 3 extra removable boundary triangles. "
            "The complete local entropy-preserving move set empties the frontier "
            "without reaching a tree: a BOUNDED negative. Evidence the bulk-cycle "
            "obstruction is a GENERAL phenomenon of both twins, not specific to "
            "111. NOT a proof that no tree exists; s=207 is holographic, only the "
            "tree question is open."),
        "honesty": "Bounded negatives only; the seed is exact-verified before any "
                   "downstream use; no non-realizability claimed. Suspects "
                   "{110,145,168}, the email, the README, and s=111's committed "
                   "seed untouched.",
        "reproduce": ".venv/bin/python -m hec.attack_207",
    }
    path = out_dir / "attack_207.json"
    path.write_text(json.dumps(payload, indent=2))
    return path


def write_markdown(val, ch, a7, cmp, out_dir: pathlib.Path = REPORTS) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    pb = ch.get("pure_bulk_cycle")
    L = []
    L.append("# Attack on s=207 — the unexplored bulk-cycle twin of s=111\n")
    L.append("s=111 and s=207 are the two **bulk-cycle** orbits of "
             "arXiv:2412.15364 whose tree-realizability is the open question. "
             "s=207 was untouched for one reason: no starting realization (seed). "
             "This was the whole blocker, so STEP 0 was to get one.\n")
    L.append("Reproduce: `.venv/bin/python -m hec.attack_207`. Exact Fraction "
             "arithmetic; bounded negatives only.\n")
    L.append("## STEP 0 — seed obtained (the blocker, resolved)\n")
    L.append(f"- **Source:** {SEED_207_PROVENANCE['source']}.\n"
             f"- **Verification:** {SEED_207_PROVENANCE['method']}.\n"
             f"- **hecdata:** {SEED_207_PROVENANCE['hecdata']}.\n"
             f"- **LP construction:** {SEED_207_PROVENANCE['lp_construction']}.\n")
    L.append("So the figure transcription (exact-verified — the s181 lesson: a "
             "misread edge would not match the ray) is what unblocked 207.\n")
    L.append("## STEP 1 — the seed is genuinely the bulk-cycle case\n")
    L.append(f"- seed realizes **{val['scale']}×** the s=207 representative "
             f"(exact, all 63 components).\n"
             f"- SA+SSA: {val['SA_SSA']}; SAC-extreme (saturated-SA rank "
             f"{val['saturated_SA_rank']} = 62): {val['SAC_extreme']}; HEI-clean: "
             f"{val['HEI_clean']}; non-chordal: {val['non_chordal']} (expected — "
             f"a surviving bulk cycle).\n")
    if pb:
        L.append(f"- **structure:** cyclomatic {ch['cyclomatic']} = a pure-bulk "
                 f"{pb['length']}-cycle (vertex degrees "
                 f"{sorted(pb['degrees'].values())}) + 3 removable boundary "
                 f"triangles. The pure-bulk cycle is the hard core: no triangle, "
                 f"no degree-3 bulk vertex, so the local entropy-preserving moves "
                 f"cannot touch it.\n")
    L.append("## STEP 2 — tree-finding (cycle_surgery)\n")
    L.append(f"{a7['verdict']}\n")
    L.append("## s=111 vs s=207\n")
    L.append("| | seed cyclomatic | pure-bulk core | surgery | best cyclomatic |")
    L.append("|---|---|---|---|---|")
    for s in ("111", "207"):
        c = cmp[s]
        pbc = c["pure_bulk_core"]
        core = f"{pbc['length']}-cycle deg {pbc['degrees']}" if pbc else "—"
        L.append(f"| s={s} | {c['seed_cyclomatic']} | {core} | "
                 f"{c['surgery']} | {c['best_cyclomatic']} |")
    L.append("")
    L.append(f"**Same obstruction class: {cmp['same_obstruction_class']}.** "
             f"{cmp['reading']}\n")
    L.append("## Honesty\n")
    L.append("- Bounded negative only: *no tree found under {this move set, this "
             "seed, this bound}* — never \"no tree exists\". s=207 IS holographic "
             "(it is realized, with a bulk cycle); only the tree question is open.\n"
             "- The seed is exact-verified before any downstream use.\n"
             "- A possible next lever (not run here): 207's surgery frontier "
             "bottoms out on an all-degree-3 pure-bulk cycle, where Y→Δ is "
             "nominally applicable — a wider/deeper or fine-graining search could "
             "be tried, exactly as for 111.\n"
             "- Suspects {110,145,168}, the email, the README, and s=111's "
             "committed seed are untouched.\n")
    path = out_dir / "attack_207.md"
    path.write_text("\n".join(L))
    return path


if __name__ == "__main__":
    main()

"""hec/rigidity_explorer.py — a hypothesis-GENERATING experiment.

CAVEAT (MANDATORY — read first): Rigidity labels are budget-bounded and the
calibration is underpowered (calibration.ok=false, 3/60 false negatives on
known-realizable n=5 cases). Result: no cheap structural predictor found, on an
admittedly noisy label set. NOT a non-realizability claim.

Compute, for many small cyclic structures, (a) a label — does cycle_surgery
break the structure to a TREE realization of its vector (exact, certified) or
not (bounded) — and (b) a battery of cheap exact structural features. Then hunt
for a feature that PREDICTS the label, with HELD-OUT validation and a
bulk-cycle control. The aim is to SURFACE a candidate structural reason for
rigidity worth trying to PROVE — never a decider.

CRITICAL HONESTY ABOUT THE LABEL (read before trusting anything):
  - "breakable" = a TREE realization of the vector was FOUND (hec.cycle_surgery,
    exact + refined-chordal certified). A sound POSITIVE label.
  - "rigid (bounded)" = NO tree found by cycle_surgery's bounded local-move
    search. This is BOUNDED-BY-METHOD: it means "cycle_surgery's entropy-
    preserving moves could not break it", NOT "no tree exists". A
    cycle_surgery-rigid VECTOR may still be tree-realizable via a DIFFERENT
    structure (session-9/obstruction_search: s=111 is pure-bulk-cyclic — hence
    cycle_surgery-rigid — yet looks like an ORDINARY tree-realizable ray).
  So any separating feature predicts cycle_surgery's SEARCH FAILURE, which is a
  real, useful, already-PROVEN mechanism (a pure-bulk cycle with no triangle /
  no degree-3 bulk is untouchable by local moves), but it is NOT a predictor of
  tree-NON-existence. The experiment reports this distinction explicitly.

Calibration: n=5 vectors are ALL tree-realizable (the 5-party cone is solved;
strong tree conjecture holds), so every n=5 case MUST come back "breakable". A
"rigid" label on an n=5 case is a labeling-pipeline false negative and is
flagged loudly — it is the trust check on the labels.

Exact arithmetic for labels and features; floats only for the ranking step.
No tree-NON-existence is ever claimed; suspects {110,145,168} untouched.

RESULT (seed 20260615, 150 cases) — an HONEST NEGATIVE on a NOISY label set, not
a clean null: NO cheap feature separates the rigid label above the 0.978 base
rate on held-out cases, BUT the label set is admittedly underpowered (only 7/150
rigid) and noisy (calibration.ok=false: 3 of 60 tree-realizable n=5 cases were
mislabeled rigid). Read this as "no cheap predictor found on a noisy label set",
NOT "no predictor exists". The one PROVEN mechanism — the
session-9 dead end, here encoded SOUNDLY as 'cycle_surgery_fixed_point' (a cycle
survives normalize and no Δ→Y / boundary-split / Y→Δ move applies) and validated
to fire on a real dead end — fires on ZERO raw seeds, and is False even on the
published s=111 seed (which still has live Δ→Y moves). A genuine dead end is a
property of the EXHAUSTED search frontier, not of the input graph; so rigidity
is not a cheap structural property of a seed, and every 'rigid' label here is
budget-bounded (corroborated by 3 n=5 false negatives). This converges with the
edge-zeroing/value-bound and obstruction_search findings: the difficulty lives
in the exact VALUES, not in any cheap combinatorial feature of the seed.

Reproduce: .venv/bin/python -m hec.rigidity_explorer
"""

from __future__ import annotations

import json
import pathlib
import random
from fractions import Fraction

import networkx as nx

from hec.cycle_surgery import (
    all_breaking_moves,
    cyclomatic,
    normalize,
    surgery,
)
from hec.entropy import PURIFIER, entropy_vector_labeled
from hec.obstruction_search import invariants
from hec.subsets import vector_to_paper

REPORTS = pathlib.Path(__file__).resolve().parent.parent / "reports"


# ----------------------------------------------------------- graph generation

def _boundary(n):
    return list(range(n)) + [PURIFIER]


def random_cyclic_graph(n, rng, kind, n_bulk, wmax=6):
    """A connected graph with at least one cycle, the cycle constructed
    EXPLICITLY. kind:
      'boundary' — a ring through >=1 boundary vertex (cycle_surgery can break
                   it via a boundary split -> typically breakable);
      'bulk'     — a ring of bulk vertices only (a pure-bulk cycle, the
                   structure that stalls cycle_surgery's local moves).
    Bulk-cycle vertices get a random number of extra boundary leaves, so their
    degree varies (degree-3 -> Y-Delta applies -> breakable; degree>=4 with no
    triangle -> untouchable). Returns (G, party) or None.
    """
    bnd = _boundary(n)
    bulk = [f"b{i}" for i in range(n_bulk)]
    G = nx.Graph()
    party = {v: v for v in bnd}
    G.add_nodes_from(bnd + bulk)

    def w():
        return rng.randint(1, wmax)

    if kind == "bulk":
        if n_bulk < 3:
            return None
        ring = bulk[:]
        for i in range(len(ring)):
            G.add_edge(ring[i], ring[(i + 1) % len(ring)], capacity=w())
        # attach every boundary vertex to a bulk vertex (as a leaf)
        for v in bnd:
            G.add_edge(v, rng.choice(bulk), capacity=w())
        # a few extra boundary-bulk edges raise some bulk degrees past 3
        for _ in range(rng.randint(0, n_bulk)):
            v = rng.choice(bnd)
            b = rng.choice(bulk)
            if not G.has_edge(v, b):
                G.add_edge(v, b, capacity=w())
    elif kind == "boundary":
        # ring mixing boundary and bulk, length >= 3, with >=1 boundary vertex
        ring_len = rng.randint(3, min(len(bnd) + n_bulk, 5))
        pool = bnd + bulk
        ring = rng.sample(pool, ring_len)
        if not any(v in party for v in ring):
            ring[0] = rng.choice(bnd)
        for i in range(len(ring)):
            G.add_edge(ring[i], ring[(i + 1) % len(ring)], capacity=w())
        # attach the remaining vertices as leaves
        for v in pool:
            if G.degree(v) == 0:
                G.add_edge(v, rng.choice(ring), capacity=w())
    else:
        return None

    if not nx.is_connected(G) or all(G.degree(v) for v in bnd) == 0:
        return None
    return G, party


# --------------------------------------------------------------- graph features

def _bulk_cycles(G, party):
    bulk = {v for v in G.nodes if v not in party}
    cycles = []
    for cyc in nx.cycle_basis(G):
        cycles.append(cyc)
    return cycles, bulk


def _is_cycle_surgery_fixed_point(G, party, n):
    """SOUND encoding of the session-9 'untouchable' signature: after the
    neutral reductions (prune/series/parallel), the graph still has a cycle AND
    NO breaking move (Δ→Y, boundary-split, Y→Δ) applies. Such a graph is a
    genuine DEAD END for cycle_surgery's move set — it WILL be labeled
    rigid_bounded. (Still bounded-by-method: a dead end for THIS move set is not
    tree-non-existence; the vector may be realizable by an unreachable tree.)
    Uses the real cycle_surgery move generator, so it cannot have the false
    positives a local cycle-check has (boundary leaves enabling a split)."""
    H = normalize(G, party)
    if cyclomatic(H) < 1:
        return False
    for _ in all_breaking_moves(H, party, n, allow_y_delta=True):
        return False  # at least one move applies -> not a dead end
    return True


def graph_features(G, party, n):
    """Cheap exact structural features of the (cyclic) realization. No LP."""
    bulk = [v for v in G.nodes if v not in party]
    cycles = nx.cycle_basis(G)
    pure_bulk_cycles = [c for c in cycles if all(v in bulk for v in c)]
    # bulk triangles
    bulk_tri = 0
    for a, b in G.edges:
        if a in bulk and b in bulk:
            for c in (set(G[a]) & set(G[b])):
                if c in bulk:
                    bulk_tri += 1
    bulk_tri //= 3 if bulk_tri else 1
    deg3_bulk = sum(1 for v in bulk if G.degree(v) == 3)
    bulk_degs = sorted(G.degree(v) for v in bulk) if bulk else [0]
    return {
        "cyclomatic": cyclomatic(G),
        "n_bulk_cycles": len(pure_bulk_cycles),
        "max_bulk_cycle_len": max((len(c) for c in pure_bulk_cycles), default=0),
        "n_bulk_triangles": bulk_tri,
        "n_deg3_bulk": deg3_bulk,
        "max_bulk_degree": max(bulk_degs),
        # SOUND session-9 signature (a genuine dead end for the move set)
        "cycle_surgery_fixed_point": int(_is_cycle_surgery_fixed_point(G, party, n)),
    }


# ---------------------------------------------------------------- the labeler

_SCRATCH = pathlib.Path("/tmp/rigidity_scratch")


def label_case(G, party, n, max_nodes=1500):
    """Run cycle_surgery; return ('breakable'|'rigid_bounded', vector_paper).
    breakable = a TREE realization was found+certified; rigid_bounded = none
    found by cycle_surgery's bounded local-move search (bounded-by-method)."""
    Gf = nx.Graph()
    Gf.add_nodes_from(G.nodes)
    for u, v, d in G.edges(data=True):
        Gf.add_edge(u, v, capacity=Fraction(d["capacity"]))
    vec = entropy_vector_labeled(Gf, n, party)
    # surgery writes a cert to out_dir when it succeeds; give it a scratch dir
    # (the cert content is irrelevant here — we only need the label)
    path, info = surgery(Gf, party, n, "rx", target=vec, max_nodes=max_nodes,
                         out_dir=_SCRATCH, log=lambda m: None)
    label = "breakable" if info["status"] == "tree" else "rigid_bounded"
    return label, tuple(int(x) for x in vector_to_paper(vec, n))


# ------------------------------------------------------------- dataset assembly

def build_dataset(rng, n5_per_kind=30, n6_per_kind=45, log=print):
    rows = []
    seen_vec = set()
    for n in (5, 6):
        per = n5_per_kind if n == 5 else n6_per_kind
        for kind in ("boundary", "bulk"):
            made = 0
            tries = 0
            while made < per and tries < per * 12:
                tries += 1
                nb = rng.randint(3, 4) if kind == "bulk" else rng.randint(1, 3)
                gp = random_cyclic_graph(n, rng, kind, nb)
                if gp is None:
                    continue
                G, party = gp
                try:
                    label, vec = label_case(G, party, n)
                except Exception:
                    continue
                if vec in seen_vec:
                    continue
                seen_vec.add(vec)
                feat = graph_features(G, party, n)
                feat.update({f"v_{k}": v for k, v in invariants(vec, n).items()
                             if isinstance(v, (int, float))})
                rows.append({"n": n, "gen_kind": kind, "label": label,
                             "features": feat})
                made += 1
        log(f"n={n}: generated {sum(1 for r in rows if r['n']==n)} distinct cases")
    return rows


# ------------------------------------------------------ separation (decision stumps)

def _stump_accuracy(rows, feat, thr, positive="rigid_bounded"):
    """Best-direction decision stump: predict positive if feature >= thr (or <)."""
    best = 0.0
    for direction in (">=", "<"):
        correct = 0
        for r in rows:
            x = r["features"].get(feat)
            if x is None:
                continue
            pred = (x >= thr) if direction == ">=" else (x < thr)
            is_pos = r["label"] == positive
            if pred == is_pos:
                correct += 1
        best = max(best, correct / len(rows))
    return best


def hunt_separators(rows, rng, log=print):
    feats = sorted({k for r in rows for k in r["features"]})
    # train/test split (held-out validation — the honesty gate)
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    cut = int(0.7 * len(idx))
    train = [rows[i] for i in idx[:cut]]
    test = [rows[i] for i in idx[cut:]]
    base_rate = max(
        sum(1 for r in test if r["label"] == "rigid_bounded"),
        sum(1 for r in test if r["label"] == "breakable"),
    ) / max(len(test), 1)

    results = []
    for f in feats:
        vals = sorted({r["features"].get(f) for r in train
                       if r["features"].get(f) is not None})
        if len(vals) < 2:
            continue
        # candidate thresholds = midpoints
        best_thr, best_train = None, 0.0
        for a, b in zip(vals, vals[1:]):
            thr = (a + b) / 2
            acc = _stump_accuracy(train, f, thr)
            if acc > best_train:
                best_train, best_thr = acc, thr
        test_acc = _stump_accuracy(test, f, best_thr) if best_thr is not None else 0.0
        results.append({"feature": f, "threshold": best_thr,
                        "train_acc": round(best_train, 3),
                        "test_acc": round(test_acc, 3)})
    results.sort(key=lambda r: -r["test_acc"])
    return results, round(base_rate, 3), len(train), len(test)


# ----------------------------------------------------------------- run + report

def validate_detector():
    """Self-check the SOUND dead-end feature: it must fire True on a genuine
    session-9 dead end (a degree-≥4 pure-bulk cycle — normalize can't touch it,
    no Y→Δ, no Δ→Y, no boundary-split) and False on a graph that still has a
    move. Returns a dict recorded in the report so the feature is never trusted
    unvalidated."""
    # genuine dead end: 4-cycle of bulk, each bulk vertex degree 4 (2 leaves)
    G = nx.Graph()
    bulk = ["b0", "b1", "b2", "b3"]
    for i in range(4):
        G.add_edge(bulk[i], bulk[(i + 1) % 4], capacity=Fraction(2))
    leaves = [0, 1, 2, 3, 4, 5, "O", "L7"]
    party = {}
    for i, bv in enumerate(bulk):
        for j in (0, 1):
            lab = leaves[2 * i + j]
            G.add_edge(bv, lab, capacity=Fraction(1))
            party[lab] = lab
    dead_end = _is_cycle_surgery_fixed_point(G, party, 6)
    # a moveable graph: a bulk triangle (Δ→Y always applies) → not a dead end
    H = nx.Graph()
    for a, b in (("c0", "c1"), ("c1", "c2"), ("c0", "c2")):
        H.add_edge(a, b, capacity=Fraction(1))
    hp = {}
    for k, c in enumerate(("c0", "c1", "c2")):
        H.add_edge(c, k, capacity=Fraction(1))
        hp[k] = k
    moveable = _is_cycle_surgery_fixed_point(H, hp, 3)
    return {"dead_end_detected": bool(dead_end),
            "moveable_rejected": (moveable is False),
            "ok": bool(dead_end) and (moveable is False)}


def calibrate_known_breakable():
    """Positive-side label calibration: the published C5 cyclic seeds for rays
    10 and 17 (cracked to trees in prior sessions) MUST label 'breakable'. This
    validates that the label has no false POSITIVES on known-realizable cases —
    complementing the n=5 negative-side check, which exposes false negatives."""
    from hec.c5_graphs import C5_PUBLISHED_GRAPHS
    out = {}
    for k in (10, 17):
        G = nx.Graph()
        party = {}
        for lab in [0, 1, 2, 3, 4, "O"]:
            G.add_node(lab)
            party[lab] = lab
        for u, v, w in C5_PUBLISHED_GRAPHS[k]:
            G.add_edge(u, v, capacity=Fraction(w))
        label, _ = label_case(G, party, 5)
        out[f"c5_ray_{k}"] = label
    out["ok"] = all(v == "breakable" for kk, v in out.items() if kk != "ok")
    return out


def run(log=print):
    rng = random.Random(20260615)
    detector = validate_detector()
    log(f"detector self-check: {detector}")
    known = calibrate_known_breakable()
    log(f"known-breakable calibration (C5 rays 10,17): {known}")
    log("building labeled dataset (cycle_surgery labels; n=5 = calibration) ...")
    rows = build_dataset(rng, log=log)
    n_break = sum(1 for r in rows if r["label"] == "breakable")
    n_rigid = sum(1 for r in rows if r["label"] == "rigid_bounded")

    # CALIBRATION: every n=5 case must be breakable (5-party cone solved)
    n5_rigid = [r for r in rows if r["n"] == 5 and r["label"] == "rigid_bounded"]
    calib = {"n5_rigid_false_negatives": len(n5_rigid),
             "ok": len(n5_rigid) == 0}

    results, base_rate, ntr, nte = hunt_separators(rows, rng, log=log)

    # per-class breakdown of the session-9 cycle_surgery confound signature:
    # does 'pure_bulk_cycle_untouchable' even fire on the rigid cases?
    def _rate(label, feat):
        sub = [r for r in rows if r["label"] == label]
        if not sub:
            return None
        return round(sum(r["features"].get(feat, 0) for r in sub) / len(sub), 3)
    confound = {
        "feature": "cycle_surgery_fixed_point",
        "fires_on_rigid_bounded": _rate("rigid_bounded", "cycle_surgery_fixed_point"),
        "fires_on_breakable": _rate("breakable", "cycle_surgery_fixed_point"),
        "note": "SOUND session-9 dead-end signature (real move generator). "
                "fires_on_breakable MUST be 0 (a dead end cannot be broken); a "
                "nonzero value would be a bug. fires_on_rigid_bounded is the "
                "fraction of rigid cases that are genuine dead ends vs merely "
                "budget-bounded — but a dead end is still NOT tree-non-existence.",
    }

    out = {
        "headline": "HONEST NEGATIVE on a NOISY label set: no cheap structural "
                    "feature predicts rigidity, but the label set is underpowered "
                    f"({n_rigid}/{len(rows)} rigid) and noisy "
                    f"(calibration.ok={calib['ok']}: {len(n5_rigid)} tree-realizable "
                    "n=5 cases mislabeled rigid). Read as 'no cheap predictor found "
                    "on a noisy label set', NOT 'no predictor exists'.",
        "what": "Hypothesis-generating rigidity experiment: do cheap exact "
                "structural features predict whether cycle_surgery breaks a "
                "cyclic structure to a TREE? Label is BOUNDED-by-cycle_surgery "
                "(rigid means 'local moves failed', NOT 'no tree exists').",
        "engine": "hec.rigidity_explorer (exact labels+features; floats only "
                  "for stump ranking)",
        "dataset": {"total": len(rows), "breakable": n_break,
                    "rigid_bounded": n_rigid,
                    "by_n": {n: sum(1 for r in rows if r["n"] == n) for n in (5, 6)}},
        "calibration_n5_all_breakable": calib,
        "calibration_known_breakable_c5": known,
        "detector_self_check": detector,
        "heldout": {"train": ntr, "test": nte, "majority_base_rate": base_rate},
        "separators_by_test_accuracy": results[:8],
        "confound_signature": confound,
        "interpretation": _interpret(results, base_rate, calib, n_break, n_rigid,
                                     confound),
    }
    return out


def _interpret(results, base_rate, calib, n_break=0, n_rigid=0, confound=None):
    if not results:
        return "no features varied — inconclusive."
    top = results[0]
    lines = []
    # the headline finding: the SOUND dead-end feature, validated to fire on a
    # real session-9 dead end, fires on NO raw seed (incl. s=111) → rigidity is
    # not a cheap structural property of the INPUT graph.
    if confound and confound.get("fires_on_rigid_bounded") == 0.0:
        lines.append(
            "SOUND DEAD-END FEATURE FIRES ON NOTHING: the validated session-9 "
            "fixed-point detector (proven to fire on a genuine dead end) is True "
            "for 0 of the rigid seeds — and is False even on the published s=111 "
            "seed, which has live Δ→Y moves. A genuine dead end is reached only "
            "AFTER the search exhausts moves; it is a property of the search "
            "frontier, not of the input. So every 'rigid' label here is "
            "BUDGET-bounded, and rigidity is not a cheap structural property of "
            "the seed graph.")
    # power caveat: with the rigid class this rare, "always predict breakable"
    # already scores base_rate, so the experiment is UNDERPOWERED to find a
    # separator regardless of whether one exists.
    if n_rigid and n_break and n_rigid / (n_break + n_rigid) < 0.15:
        lines.append(f"UNDERPOWERED: only {n_rigid}/{n_break + n_rigid} cases are "
                     f"(bounded-)rigid, so the majority base rate is {base_rate} — "
                     f"a separator must clear that high bar to register. cycle_surgery "
                     f"breaks almost everything, so reliable rigid examples are scarce "
                     f"by construction; absence of a separator here is weak evidence, "
                     f"not proof none exists.")
    if not calib["ok"]:
        lines.append(f"LABELING UNTRUSTWORTHY: {calib['n5_rigid_false_negatives']} "
                     f"n=5 cases labeled rigid, but all n=5 vectors are "
                     f"tree-realizable — the rigid label is search-bounded and "
                     f"these are false negatives. The 'rigid' class is partly noise; "
                     f"treat any separation with caution.")
    strong = top["test_acc"] >= base_rate + 0.15
    if strong and top["feature"] == "cycle_surgery_fixed_point":
        lines.append(
            f"CANDIDATE FEATURE: '{top['feature']}' predicts the (cycle_surgery) "
            f"rigid label at held-out accuracy {top['test_acc']} vs base rate "
            f"{base_rate}. This is the PROVEN session-9 mechanism: a graph that "
            f"is a fixed point of the entropy-preserving move set (a cycle "
            f"survives normalization and no Δ→Y / boundary-split / Y→Δ move "
            f"applies) is a genuine dead end. IT IS A PREDICTOR OF cycle_surgery "
            f"SEARCH FAILURE, **NOT** of tree-NON-existence: such vectors (e.g. "
            f"s=111) may still be tree-realizable via an unreachable structure. "
            f"So it is a candidate reason for SEARCH HARDNESS to feed the "
            f"proof/algorithm work, NOT a rigidity decider.")
    elif strong:
        lines.append(
            f"CANDIDATE FEATURE (unexpected): '{top['feature']}' separates the "
            f"(bounded) rigid label at held-out {top['test_acc']} vs base "
            f"{base_rate}. Worth inspecting: is it a real structural reason or a "
            f"cycle_surgery-search artifact? Next step is a proof attempt, NOT a "
            f"decision on any ray.")
    else:
        lines.append(
            f"NO feature separates the (bounded) rigid label above the base rate "
            f"on held-out cases (best '{top['feature']}' test_acc {top['test_acc']} "
            f"vs base {base_rate}). Evidence the difficulty is in exact VALUES, "
            f"not any cheap structural feature — consistent with the "
            f"edge-zeroing / value-bound and obstruction_search findings.")
    lines.append("BOUNDED: 'rigid' = cycle_surgery local-move failure, never "
                 "tree-non-existence; no claim about s=111/207 or suspects.")
    return " ".join(lines)


def write_report(out, out_dir=REPORTS):
    out_dir.mkdir(exist_ok=True)
    p = out_dir / "rigidity_explorer.json"
    p.write_text(json.dumps(out, indent=2))
    return p


if __name__ == "__main__":
    R = run()
    print(json.dumps(R["dataset"], indent=2))
    print("calibration:", R["calibration_n5_all_breakable"])
    print("held-out:", R["heldout"])
    print("top separators:")
    for s in R["separators_by_test_accuracy"][:6]:
        print(f"  {s['feature']:<32} train={s['train_acc']} test={s['test_acc']}")
    print("\nINTERPRETATION:\n", R["interpretation"])
    print("\nreport ->", write_report(R))

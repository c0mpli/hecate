# Lab notebook

Newest entries first. Every claim here must be reproducible from a command in
this repo.

## 2026-06-15 — Session 16: rigidity_explorer — NO cheap predictor of rigidity found, ON AN ADMITTEDLY NOISY / UNDERPOWERED LABEL SET (calibration.ok=false); SOUND dead-end detector fires on 0 seeds incl. s=111; committed with mandatory caveat

**HEADLINE (honest negative, labeled as honest): no cheap structural feature
predicts rigidity — but this is reported on a NOISY, UNDERPOWERED label set, NOT
as a clean null result.** The experiment self-reports `calibration.ok=false`: 3
of 60 n=5 cases (all of which are tree-realizable) were mislabeled rigid, so the
rigid class is partly noise; and only 7/150 cases are rigid, so the experiment
is underpowered (a separator must beat a 0.978 base rate). The honest reading is
"no cheap predictor found on an admittedly noisy label set," NOT "no predictor
exists." COMMITTED WITH THIS MANDATORY CAVEAT, carried both here and as a comment
block atop `hec/rigidity_explorer.py`: rigidity labels are budget-bounded and the
calibration is underpowered (calibration.ok=false, 3/60 false negatives on
known-realizable n=5 cases); no cheap structural predictor found, on an admittedly
noisy label set; NOT a non-realizability claim. (README left untouched per the
standing constraint.)

**Asked for a hypothesis-GENERATING experiment: label many small cyclic graphs
breakable (cycle_surgery found+certified a TREE) vs rigid_bounded (its bounded
local-move search did not), compute cheap EXACT structural features (no LP), and
hunt — with held-out validation + a bulk-cycle control + calibration on known
cases — for a feature predicting rigidity, as a HYPOTHESIS to later prove, never
a decider. Result: no cheap structural feature separates; the one PROVEN
mechanism is not a property of the input graph. Held uncommitted for review.**

Reproduce: `.venv/bin/python -m hec.rigidity_explorer`
(report → `reports/rigidity_explorer.json`; tests `tests/test_rigidity_explorer.py`).

**Dataset (seed 20260615):** 150 distinct-vector cases, both n=5 and n=6, two
generators (pure-bulk-ring 'bulk', mixed boundary-ring 'boundary'). 143
breakable / 7 rigid_bounded. The label is asymmetric: breakable is SOUND (a
certified tree); rigid_bounded is BOUNDED-BY-METHOD only.

**Calibration (the trust checks ran BEFORE believing anything):**
- positive side — published C5 seeds rays 10 & 17 (cracked in prior sessions)
  both label breakable ✓ (no false positives on known-realizable cases).
- negative side — 3 of 60 n=5 cases label rigid_bounded, but ALL n=5 vectors are
  tree-realizable ⇒ these are cycle_surgery FALSE NEGATIVES. So the rigid class
  is partly noise; the experiment flags this loudly (`calibration.ok=false`).

**The one proven mechanism, encoded SOUNDLY and VALIDATED:** the session-9
"untouchable" signature became `cycle_surgery_fixed_point` — TRUE iff after
`normalize` a cycle survives AND the real move generator yields NO breaking move
(Δ→Y / boundary-split / Y→Δ). `validate_detector()` confirms it: fires True on a
hand-built genuine dead end (degree-4 pure-bulk 4-cycle), False on a moveable
bulk triangle. (Replaces an earlier LOCAL cycle-check that had false positives —
it fired on 4 breakable cases because boundary leaves enable a split; the
fixed-point check, using the actual generator, cannot have that error.)

**Headline result:** the validated dead-end feature fires on **0 of 150** seeds
— `fires_on_breakable = 0.0` (required for soundness) AND `fires_on_rigid = 0.0`.
It is False even on the published **s=111** seed, which still has 3 live Δ→Y
moves. A genuine dead end is reached only AFTER the search exhausts moves — it is
a property of the EXHAUSTED frontier, not of the input graph. So every rigid
label here is BUDGET-bounded, and rigidity is NOT a cheap structural property of
a seed. Supervised hunt agrees: no feature beats the 0.978 majority base rate on
held-out cases (best `max_bulk_degree` test_acc 0.978 = base). Experiment is also
honestly UNDERPOWERED (7 rigid, 3 of them noise) — absence of a separator is
weak evidence, not proof none exists.

**Conclusion:** third independent line (after the cut-feasibility filter and
obstruction_search, both same week) converging on the same verdict — s=111's
difficulty lives in exact VALUES / search-reachability, not in any cheap
combinatorial feature of a seed. No claim of tree-non-existence anywhere; "rigid"
is always cycle_surgery-bounded; suspects {110,145,168} and s=111/207 untouched.
Per protocol: HELD UNCOMMITTED pending review.

## 2026-06-15 — Session 14: hec/obstruction_search.py — cheap LP-free test of whether s=111 is SPECIAL or just HARD → it's ORDINARY (no separator)

**Flipped the question.** Instead of searching (and failing) for a tree
realization of the bulk-cycle orbit s=111, asked whether any cheap, LP-free
vector/structural INVARIANT separates 111 from every ray KNOWN to be
tree-realizable. A separator would be a REASON (a candidate obstruction → a
possible strong-tree-conjecture counterexample); no separator is evidence 111
is an ordinary tree-realizable ray the search was merely too slow to crack.
`hec/obstruction_search.py` + `tests/test_obstruction_search.py`; report in
`reports/obstruction_search.{json,md}`. Reproduce: `.venv/bin/python -m
hec.obstruction_search`. Uncommitted (held for review, per the session-11→13
pattern).

**KEY FINDING that reshaped the control — chordality is the "bulk-cycle TRAP",
quantified: 104 of the 148 tree-realizable n=6 orbits are THEMSELVES
non-chordal.** So the chordality criterion (simple-forest iff) does NOT
distinguish tree-realizable from not at n=6 — most tree-realizable rays need
NON-simple trees. This means the honest control cohort for 111 is not just the
two n=5 rays 10/17 but a **104-strong, same-n, non-chordal-but-tree-realizable**
set. The prompt's warned-against confound ("invariant just detects has-a-cycle")
is therefore real and measurable: any invariant flagging 111 must NOT flag those
104 (or 10/17).

**RESULT — NO cheap invariant separates s=111.** A 21-invariant battery across
the four requested families (correlation-hypergraph/line-graph shape;
cut-value/saturation profile; PMI/independence; clique/hole structure), all
exact integer/graph-structural, no LP, no weight fit. On EVERY non-degenerate
invariant s=111 lies INSIDE the cohort range; across the 17 discriminating
same-n invariants it sits at **percentiles 27–91** of the 104 tree-realizable
rays — strictly interior, usually near the median (e.g. induced-4-hole count
111=6 vs cohort mean 6.12; hole density 0.111 vs mean 0.119). The C5 controls
10/17 are inside every n-agnostic range (control passes). **Verdict: 111 looks
like an ORDINARY non-chordal tree-realizable ray — evidence it is merely HARD,
not a structural counterexample. Points back to the search filter (the angle-1
filter), NOT to a non-realizability claim.**

**s=207 (secondary): MARGINAL only, honest caveat.** 207 sits just past the
cohort edge on 3 count-type invariants (42 vs max 40 induced 4-holes; 0.737 vs
0.714 hole density; 119 vs min 123 SA-saturated). The cohort edge is itself a
tree-realizable ray, so this is the high-density END of a continuum, not a clean
gap — weak, single-boundary, and 207 has no studied cyclic seed. NOT a candidate
obstruction in the strong sense; it does prove the test isn't trivially
returning "inside" for everything (it discriminates).

**Degenerate invariants surfaced (no signal, flagged transparently):** the
single-label pairwise MI is uniformly ZERO across this whole family (every
S(ij)=S(i)+S(j); 21/21 vanishing at n=6), so the coarsest PMI layer and
"independent parties" carry no information — the correlation hypergraph's B-sets
(over larger subsets) are the right object, and they don't separate either. The
non-chordal core (simplicial-elimination residue) equals the WHOLE line graph
for every ray (these hypergraphs are near-cliques, clique# ≈ 50/54), so it too
is non-discriminating.

**Honesty:** correlation is never proof — no non-realizability claimed from any
invariant; "no separator" means none in THIS battery, not that none exists;
111/207 ARE holographic (realized, with a bulk cycle), only the tree question is
open; suspects {110,145,168} not analyzed; email/README untouched. Two latent
bugs avoided by validation: optimized exact 4-hole count is regression-tested ==
brute force; percentile centrality computed within the SAME-n cohort to avoid an
n-pooling artifact. 8 new tests; full suite 54 green; day-1 regression passes.

## 2026-06-12 — Session 10: multi-seed 111 experiment (seed-specific vs intrinsic?)

**Question:** is the pure-bulk-4-cycle wall cycle_surgery hit on s=111 a
property of that ONE realization, or intrinsic to the ray? **Built
hec/seed_search.py** to test it: generate structurally-distinct cyclic
realizations of the SAME ray (stabilizer images — relabelings fixing the
63-vector — plus LP fits on varied topologies; pynauty-deduped, each
Fraction-verified to realize a multiple of the ray), run surgery on each.
Added a party-BLIND `structure_key` so symmetry copies are counted as the
SAME independent structure (not double-counted).

**Machinery validated on C5 ray 10:** 3 distinct seeds generated (base + 2
stabilizer images), **3/3 reduce to trees**. Tests in test_seed_search.py
(stabilizer image realizes the same ray exactly; surgery reduces it;
structure_key collapses symmetry copies).

**111 result — the honest THIRD outcome: INCONCLUSIVE, bounded by seed
generation.** Not "a seed reduced" (seed-specific) and not "all diverse
seeds failed" (evidence intrinsic) — instead: **only ONE independent bulk
structure could be generated at n=6.** hecdata has exactly 1 row in 111's
orbit (line 294); `lp_realize_target` found 0 realizations of 111 in
repeated tries (152 s, 0/4); the ray's stabilizer has only 4 elements and
yields structurally-identical symmetry copies. So the 2 seeds tested span 1
independent structure. Both: full entropy-preserving move-closure searched
EXHAUSTIVELY (frontier emptied at 10 nodes), no tree; surviving obstruction
= the pure-bulk degree-4/5 4-cycle, provably untouchable by the COMPLETE
local move set.

Interpretation (logged to reports/bulk_cycle_attempts.jsonl, qualified):
the one reachable realization of 111 is irreducible under all local
entropy-preserving operations — but with only 1 independent structure
testable, this does NOT distinguish "intrinsic to the ray" from "shared by
the one realization we can reach." The cheap seed-diversity test is
INCONCLUSIVE here precisely because independent n=6 realizations are hard to
generate — which is itself the signal that the **ray-level fine-graining
exclusion engine (Track B)** — seed-independent, working from the entropy
vector rather than a graph — is the tool actually needed to settle 111.
Explicitly NOT a non-existence claim (111 IS holographic; it's realized,
just with a cycle). s=207: still no seed.

**Next:** build the fine-graining exclusion engine (chordal fine-grainings
up to a bound N′; arXiv:2512.18702 §non-chordal) — the principled, seed-
independent settle for both the bulk-cycle pair and (later) the suspects.
Still gated behind the SPEC §8 email.

## 2026-06-12 — Session 9: hec/cycle_surgery.py — bulk-cycle rays 10/17 CRACKED

**The directed-surgery lever works where all blind search failed.**
hec/cycle_surgery.py implements the EXACT entropy-preserving graph operations
of arXiv:2204.00075 §graph-operations: Δ→Y (lem:triop, w_σi=w_ij+w_ik, …),
its inverse Y→Δ (halves, needs triangle inequalities), series (degree-2 bulk
→ min edge), parallel (sum), pendant prune, and boundary-vertex split — each
provably min-cut-preserving AND re-verified exactly (Fraction) after every
move. Best-first search on cyclomatic number, pynauty-canonical dedup,
node/depth bounded.

**GATE PASSED — C5 rays 10 and 17.** These are the surviving-bulk-cycle rays
that the blind annealer (1/8) and the keep/discard search.py (8/10) BOTH
missed. Surgery turns their cyclic models into **trees**: ray 10 in 10 moves
(47 nodes, scale 2), ray 17 in 10 moves (28 nodes, scale 1) — independently
re-verified (forest, exact). The move traces are exactly the "judicious
iterative Δ-Y" 2204.00075 describes (Δ→Y, Y→Δ, boundary splits interleaved).
CI test `tests/test_cycle_surgery.py` guards the gate + per-move exactness.
(C5 trees are known — 2204.00075 fig N5trees — so these are TOOL VALIDATION,
not novel; certs go to the gitignored surgery_validation/.)

**s=111 — BOUNDED no-reduction (honest, NOT a non-existence claim).** From
the hecdata cyclic seed (cyclomatic 3), surgery killed 2 of 3 cycles (3→1)
then stalled. The survivor is a **pure-bulk 4-cycle [x1,x2,x3,x4], all
vertices degree 4–5** — no bulk triangle (Δ→Y needs one), no degree-3 bulk
(Y→Δ needs that), boundary-split cannot reach a pure-bulk cycle, and
bulk-vertex splitting is NOT entropy-preserving (more cut freedom only
lowers entropies). So the COMPLETE local entropy-preserving move set cannot
touch this cycle — the genuine hard wall, same class as N6er3 (which
2204.00075 also left unresolved). Logged to reports/bulk_cycle_attempts.jsonl
strictly as "no reduction under {move set, bound}, this seed". This is
IMPORTANT DATA toward 111's realization possibly needing the cycle — to be
settled by the fine-graining exclusion engine (Track B), or by trying
alternative cyclic seeds. It is NOT "111 is non-realizable" (it IS
holographic — it's realized, just with a cycle) and NOT "no tree exists".

**s=207** — no cyclic seed (absent from hecdata; a newer orbit) → skipped
until a seed exists (e.g. from arXiv:2412.15364 ER_graphs or a fresh
realization).

**Net:** cycle_surgery.py is validated and is the first tool here to resolve
the bulk-cycle subclass on the solvable (C5) cases. For the actual n=6
targets it gives an honest bounded wall on 111's known realization, which
sharpens the next step: Track B (bounded chordal fine-graining = exclusion-
grade) or alternative-seed surgery. 111/207 remain correctly unclaimed.

## 2026-06-12 — Session 8: hec/search.py (autoresearch-shaped keep/discard loop)

**Built `hec/search.py`** — Track A for the bulk-cycle pair s=111/207, in the
karpathy/autoresearch keep/discard SHAPE (no neural net): mutated artifact =
a candidate graph; the "metric" = our EXACT LP fitter + ray-match; program.md
= the `POLICY` dict at the top (the one place a human edits); keep-if-improved
= keep-if-lower-score with an exact success gate. Hard rules enforced in code:
floats only rank, Fraction-exact certifies; SUCCESS writes a self-certifying
cert with the realized 63-vector; FAILURE logs only "no tree found under
<policy, budget>", never "no tree exists".

**The design fix over the failed blind annealer (1/8):** seed from a graph
that ALREADY realizes the ray (a published cyclic model) and walk
entropy-preserving moves (Δ-Y, vertex/purifier splits, edge removal) that
reduce the cyclomatic number, the LP fitter re-certifying realization each
step. Score = 100·κ(certified graph) if realizing, else 1000+slack; SUCCESS =
realizing AND κ=0 (forest). Stays on the realizes-the-ray manifold, drives
cycles → 0. Crucially, the LP may zero out a cycle edge, so the certified
(pruned) graph can be a forest even when the search topology wasn't — a free
win path.

**Real Δ-Y seed for s=111 obtained** (`scripts/extract_bulk_seeds.py`):
matched 111's Sym(7) orbit against the 4144 HEC6 graph models in the hecdata
repo (SergioHC95) — line 294 — relabeled to our representative and verified
exact (`data/targets/bulk_cycle_seeds.json`). s=207 is NOT in hecdata (likely
one of He-Hubeny-Rota's 25 NEW orbits, post-dating that repo) → falls back to
random seeds, flagged. (Parse bug caught: hecdata uses an explicit "O"
purifier vertex in 4126/4145 graphs; my first regex char class omitted "O"
and silently dropped every purifier edge → zero matches. Fixed.)

**LADDER GATE (binding): C5 rays 10-19 — RESULT: 8/10, but the 2 misses
are the decisive ones.** `scripts/search_ladder.py`. Trees found for
11,12,13,14,15,16,18,19 (all 8 BOUNDARY-cycle rays — those whose cycles a
boundary split removes); MISSED 10 and 17 (the 2 rays whose BULK cycle
survives splitting) within a 6000-iter / 700 s budget. A 5× improvement over
the blind annealer's 1/8, and the loop reliably does boundary-cycle → tree.

**But this does NOT clear the gate for 111/207.** Rays 10 and 17 are the
exact analogues of the targets: 111/207 also have surviving BULK cycles, and
the loop failed precisely the bulk-cycle subclass (0/2). So per policy the
loop does NOT run on 111/207 with any claim — the same discipline that
halted tree_search.py. The gap is the unchanged hard core: breaking a
pure-bulk cycle needs a Δ-Y / bulk-split sequence the keep/discard search
doesn't reliably find within budget, even though its move set includes them.
The next lever is targeted bulk-cycle surgery (enumerate Δ-Y on each bulk
3-cycle; for longer bulk cycles, chord-then-Δ-Y), or the fine-graining
machinery — NOT more blind iterations.

Found bugs en route (both fixed): (1) the verifier discarded a candidate's
own realizing weights and re-fit from scratch — added a current-weights fast
path so seeds / entropy-preserving moves are recognized exactly and cheaply;
(2) restarts picked uniformly among 4 seeds, diluting the single realizing
cyclic seed 3:1 with useless random trees — ray 11 missed at 701 s under one
RNG yet solved in 4 candidates under another. Biasing restarts to cyclic
seeds + best-realizing-so-far fixed it (ray 11 then solved under the failing
RNG in 255 candidates). Smoke + CI test (`tests/test_search.py`) guard the
loop end-to-end; every found tree is exact-certified and the C5 ones were
independently re-verified (forest, exact, scale 1).

**Net for the campaign:** hec/search.py is a real, validated tool for
boundary-cycle tree realization (8/8) and a scaffold for the bulk-cycle case,
but it is NOT yet validated where it counts (bulk cycles, 0/2). 111/207
remain correctly untouched, gated behind both the bulk-cycle capability and
the email.

## 2026-06-12 — Session 7: bulk-cycle pivot (new lead target, T2)

**The 2 bulk-cycle orbits are s=111 and s=207** (arXiv:2412.15364
§graphERs footnote: their graphs "still each contains a bulk cycle, and it
would be interesting to see if we can alternatively realize them by tree
graphs. We leave this for future exploration"). This is the SPEC's T2 and
the new lead, ahead of the {110,145,168} suspects — self-contained,
publishable either way, low scoop risk. Saved with provenance to
`data/targets/bulk_cycle_orbits.json`.

Both validated exactly: SA+SSA, SAC-extreme (rank 62), HEI-clean (0
violations — they ARE holographic, just cyclic), non-chordal (no simple
forest — the expected sanity result; a bulk cycle survives boundary
splitting, unlike rays 11-16/18/19). NOT mystery orbits — these are realized
holographically; the open question is purely topological (tree vs cycle),
which bears directly on the strong tree conjecture of arXiv:2204.00075.

**Track A tooling built (`hec/tree_search.py`): party-splitting tree
annealer.** Non-simple tree = parties may label several leaves, tree
topology throughout. The LP fitter is pattern-agnostic so we reuse
lp_realize's slack/hard LPs and add only labeled min-cut patterns +
labeled exact certification (`entropy_vector_labeled`). **Fitter
oracle-validated:** recovers exact weights on all six known C5 split-trees
(11,12,13,16,18,19) in 0-3 s. Annealer = SA over tree space (add/prune bulk,
split/merge party copies, regraft), fitness = best fitter slack; optional
seed from a cyclic graph's boundary-split (the real 111/207 workflow:
split → break surviving bulk cycle).

**GATE RESULT: the from-scratch annealer FAILS the ladder — 1/8** (rays
11-16,18,19; 6 restarts × 500 iters each). Only ray 13 produced anything,
a valid non-simple FOREST (exact, 2 components — acceptable per 2512.24490).
The other 7 returned nothing: not a tuning gap but a structural one — blind
search over labeled-tree space with split/regraft moves doesn't converge,
because the LP-slack landscape is flat until a topology is almost exactly
right (the Sparse Oracle Principle cuts the other way here: sparse trees fit
instantly GIVEN the structure, but finding the structure among all labeled
trees is the hard part). **Per policy this is NOT evidence about 111/207,
and the annealer does NOT run on them.** The labeled LP fitter itself is
sound (oracle-validated 6/6) — only the topology search is weak.

**Track A re-scoped (the honest next build).** Rung-1 EXISTENCE is already
settled independently of the annealer: boundary-splitting the published
cyclic models (hec/splits, session 5) gives verified non-simple trees for
8/10 C5 rays. The annealer added nothing there. The genuinely open
subproblem is **breaking a SURVIVING bulk cycle** — C5 rays 10, 17 and the
targets 111, 207, where splitting leaves a pure-bulk cycle. Blind annealing
can't do it; the right tools are (a) explicit entropy-preserving graph
operations (Δ-Y exchange + generalizations, arXiv:2204.00075 §gops) applied
to the cyclic model, or (b) the chordal fine-graining machinery (which is
also Track B's exclusion engine). Both are real builds, appropriately so —
this is the exact subproblem the literature flags as hard (HHR: tree
constructions for bulk-cycle rays "have so far failed"; 2204.00075 left
N6er3 unresolved). Validation target for whichever tool: C5 ray 10 or 17
first (trees known to exist via Δ-Y), THEN 111/207.

Status: targets identified + validated, tooling scaffolded, no result
claimed. The campaign is correctly gated behind the email.

## 2026-06-12 — Session 7: STEP-0 minimal-claim audit (gates the email)

**All minimal-model claims CONFIRMED, apples-to-apples** (`scripts/
verify_minimal_claims.py`, now CI-guarded in `tests/test_hlo.py`). Internal
vertex ≝ nonzero-degree non-boundary vertex; edge ≝ nonzero-weight edge —
identical definition for paper and ours. Figure 7 of arXiv:2601.19979
(`graph_realizations2.png`) independently confirms the paper baselines:
146 shows internal vertices 1–11, 180 shows 1–7, 181 shows 1–10.

| ray | paper (edges / internal / scale) | ours (edges / internal / scale) |
|-----|----------------------------------|---------------------------------|
| 146 | 36 / 11 / 12 | **27 / 10 / 1** |
| 180 | 25 / 7 / 12  | 25 / 7 (no reduction) |
| 181 | 29 / 10 / 9  | **22 / 7 / 1** |

All exact, all simple-but-cyclic. Note the scale: our models realize the
ray at scale 1 (integer weights), the paper's at 12/12/9 — same extreme ray
(defined up to positive scaling), ours strictly smaller in vertices, edges,
AND weights. Honest email phrasing: "a smaller graph realizing the same
ray" — never imply the paper's is wrong (it isn't; minimization wasn't their
goal). 181's N=18 is the RL vertex budget; its realized graph uses 10
internal (one budget vertex unused) — we compare against realized counts.

**Caught in QA, not in the claim:** the first audit run reported our models
as non-realizing — a bug in the *checker*: certificates serialize vertices
via `str()`, so parties become "0".."5"; rebuilding without mapping them
back to int left the parties isolated. The stored models were always exact
(written through `_certify`). Lesson: when a verifier rebuilds a graph from
serialized data, normalize labels before trusting a mismatch.

## 2026-06-12 — Session 6: items 4–6 (HLO verify / oracle / minimize) → v0.2.0

**Item 4 — independent verification of arXiv:2601.19979, all three EXACT.**
Their conventions decoded from the repo source (complete-graph weights, lex
pair order, parties = vertices 0–5, purifier = N−1): repo pinned at
`193d994c8b3a`. The paper's explicit edge lists for s ∈ {146, 180, 181}
transcribed into `hec/hlo_data.py` and verified in exact arithmetic:
**S = 12×, 12×, 9× the target rays respectively.** Topology classes
recorded: all three are simple (one boundary vertex per party) and CYCLIC —
the chordality tripwire is clean (a verifying simple forest would have
contradicted the theorem; none did). Their mask-order targets equal ours
component-by-component — the two data lineages agree.

Nuance worth knowing: the REPO's ray-146 artifact is float-only (cosine
0.9999999938, "near-perfect"); the PAPER has an exact integer model found by
hand from the RL output. Before reading the paper closely we independently
ran LP weight-recovery on the float support and obtained an exact
realization with **27 edges (vs the paper's 36)** — not a novelty (the paper
got exactness first) but an independent confirmation by a different method,
and a sparser model (`reports/realizations/n6_s146_EXACT.json`).

**Item 5 — oracle treatment at n=6: 3/3 recovered.** Weights stripped from
the verified topologies, fit_weights recovers exact weights: s=180 attempt
1 (3 s), s=181 attempt 5 (15 s), s=146-support attempt 9 (31 s). The LP
realizer is calibrated at n=6 on real frontier targets: given the right
topology it closes quickly — consistent with the Sparse Oracle Principle.

**Item 6 — minimization pass (greedy bulk-deletion + LP refit; upper
bounds only, no minimality claims):** s=146: **10 internal vertices**
(paper: 11; 27 edges). s=180: 7 (no reduction; paper's 7 stands). s=181:
**7 internal vertices** (paper: 10; 22 edges vs their 29 — three vertices
and seven edges lighter). Exact certificates:
`reports/realizations/n6_s{146,180,181}_minimal.json`.

**Item 7 — status fields:** `data/targets/mystery_orbits.json` now carries
per-orbit status ({146, 180, 181} realized + verified; {110, 145, 168} open,
non-realizability conjectured) and the HLO provenance pin. README M3 row
and Data & references updated with the explicit commit hash.

**Paper context recorded:** HLO's evidence for non-realizability of
{110, 145, 168} is reward-landscape adjacency (surrounded by HEI-violating
rays) + RL failure to 13 internal vertices; they note the Avis–Cuenca
finiteness bound for n=6 is 1,422,564 vertices — exhaustion is not a
practical exclusion route; a separating HEI is.

## 2026-06-12 — Session 5 addendum 2: rung-1 oracles, N6er cross-ref, gate survey

**Rung-1 oracle set, mostly DERIVED rather than transcribed:** the labeled
engine (`entropy_vector_labeled`) now supports non-simple models. Splitting
every multi-degree boundary vertex of our verified published C5 models
(`hec/splits.py`, the fig:N5trees transform) preserves the entropy vector
EXACTLY for all ten non-chordal rays and yields verified non-simple TREES
for eight (11–16, 18, 19) — same QA bar as transcription, machine-checked.
Rays 10 and 17 keep pure-bulk cycles after splitting (the Δ-Y class) — they
are the hard rung-1 validation targets; their fig:N5trees rows remain to be
transcribed (or beaten by the annealer) next session.

**~14 tree-resistant models cross-ref (report):** only two are public —
figs. N6er1/N6er3 of 2204.00075. Both transcribed and verified (SA+SSA
hold, bulk 4-cycles as advertised; `hec/n6er_data.py`). NEITHER is among
the 208: saturated-SA ranks 58 and 61 < 62, i.e. they are HEC₆ extreme rays
with higher-dimensional PMIs, structurally outside the SSA-compatible
SAC₆-extreme stratum. Zero overlap with {110, 145, 168}. The other ~12
identities are not published (the 4122-ray "n6wip" dataset). The HHR
bulk-cycle pair (2 of the 150, which ARE in the 208) is therefore a
DIFFERENT pair — extract their s-indices from 2412.15364's tables next
session. **Bonus target:** 2204.00075 explicitly failed to tree-convert
N6er3; a verified tree for its vector resolves an open item of that paper —
prime annealer target after rung 1.

**Non-simple gate survey (2512.18702 §non-chordal-case):** no closed-form
necessary condition exists for non-simple-tree realizability. The
characterization: S is non-simple-tree realizable iff SOME fine-graining S′
(party-splitting, N′ > N) has chordal PMI — then Algorithm 1 builds the
tree upstairs and relabeling descends. The paper leaves the search over
fine-grainings open (choice of CG-map, free components of S′). This IS the
rung-2 track-2 machinery: bounded-N′ exhaustion of chordal fine-grainings =
exclusion-grade evidence of tree-unrealizability. Implementation is a
rung-2 deliverable, not a quick gate.

**Rung-2 is two-track (user directive):** (a) tree equivalent for the HHR
pair = win; (b) bounded-exclusion of chordal fine-grainings = bigger win —
exclusion-grade machinery only, never annealing absence.

## 2026-06-12 — Session 5 addendum: items 1–3 closed

**19/19 transcriptions verified** — fig 12 finally fell to the fig-18
lesson applied to itself: its stacked "11" label is two labels, the figure
has 16 unit edges (central hub b5 joined to b1–b4, every boundary vertex on
two bulks), scale 2. All searches had been constrained to 15 edges. Locked
into the suite (`tests/test_c5_graphs.py`).

**19/19 certificates in reports/realizations/**: 16 fully independent
(13 LP cold + 3 annealed), 3 second-tier with explicit provenance
(rays 10, 12, 19 — published topology credited, weights via LP recovery).

Transcription craft notes for next time (n=6 figures will be worse):
count LABELS not lines; stacked digits are separate labels; lines pass
through vertex positions without terminating; batched PDF reads can shuffle
document order — always adjudicate entry↔figure by orbit-matching against
all candidate rays.

## 2026-06-12 — Session 5: the chordality gate (pre-campaign report)

**Papers ingested:** arXiv:2512.18702 + 2512.24490 (Hubeny–Rota, Dec 2025;
building on 2412.18018). Main theorem of 2512.24490: an entropy vector
obeying SA+SSA is realizable by a holographic **simple forest** (one
boundary vertex per party, no cycles) **iff the line graph of its
correlation hypergraph is chordal** — necessary AND sufficient, with a
constructive tree-builder when it passes. Implemented in
`hec/chordality.py` (exact arithmetic end-to-end).

**Calibration (19 C5 rays):** rays 1–9 chordal (exactly the published
simple-tree models: stars 1–7, double-stars 8–9); rays 10–19 NOT chordal —
exactly the rays whose published and engine-found models all carry cycles.
19/19 agreement with ground truth. Corollary worth noting: rays 10–19
provably admit no simple-forest model, so IF the strong tree conjecture
(2204.00075) holds they must be realizable by NON-simple trees — a concrete,
falsifiable target for the upgraded annealer at n=5.

**THE GATE RESULT — all six mystery orbits FAIL chordality:**
s ∈ {110, 145, 168} (suspects) and s ∈ {146, 180, 181} (HLO-realized):
none is realizable by any simple forest. Theorem-grade, certificate =
rerun `hec.chordality.simple_forest_realizable` on the targets.

What this does and does not say:
- It does NOT kill any suspect: {146, 180, 181} also fail yet ARE
  holographic (HLO's graphs must therefore be non-simple-tree/cyclic —
  consistency check passed).
- It DOES collapse Track A's search space: simple trees are provably dead
  for the suspects. Any realization is a non-simple tree (parties labeling
  several boundary vertices) or carries bulk cycles. If the strong tree
  conjecture holds and the suspects are holographic, the realization is a
  non-simple TREE — so Track A must add party-splitting moves (duplicate
  boundary vertices per party) to the annealer BEFORE the campaign; the
  current engine cannot represent the only tree class left.
- 2512.18702's coarse-graining/fine-graining machinery ("detection of
  unrealizability independently of HEIs") is the natural Track B companion
  and is now in the reading queue with the source in data/raw/.

**Calibration relabeled (epistemics):** rays 1–9 are the must-pass
verification set (published simple trees ⇒ chordality must hold; failure =
bug). Rays 10–19 non-chordal are **derived facts** — new, criterion-
dependent claims, consistent with 2204.00075 (which needed non-simple trees
for exactly the non-tree-realized rays) and with every cyclic model our
engines produced, but verified by nothing prior. Tests encode the split.

**Constructive tree-builder run end-to-end** (`hec/tree_builder.py`,
Algorithm 1 of 2512.18702): for all nine chordal rays, built the simple
forest from the entropy vector alone (positive B-sets → line graph →
clique tree → leaf attachment → edge weights by the split rule) and
recomputed entropies exactly — **9/9 exact matches**; rays 1–7 emerge as
the single-hub stars, 8–9 as the double-stars, recovering the published
structures from pure entropy data.

**Novelty pre-check (NEGATIVE — C5 rung is validation-only):**
2204.00075's fig. N5trees already exhibits non-simple tree realizations for
every HEC₅ extreme ray lacking one ("the conjecture has been confirmed for
N=5", 2512.18702 §discussion). No novelty claim attaches to C5 trees, ever.
Bonus intel from the same scan: circa 2022 only ~14 of 4,122 then-known
HEC₆-candidate graph models resisted conversion to trees (one explicit
stubborn case: fig. N6er3 of 2204.00075), and 2512.18702 reports that tree
constructions for some bulk-cycle rays "have so far failed" — the HHR
bulk-cycle rung of the ladder is genuinely open research.

**Validation ladder for the annealer upgrade (party-splitting moves) —
no rung skipped, each rung gates the next:**
1. C5 rays 10–19: reproduce non-simple trees (known to exist — validation).
2. HHR bulk-cycle pair (2412.15364): tree-equivalents — OPEN (attempts in
   the literature failed; a hit here is a result).
3. HLO triple {146, 180, 181}: tree-equivalents of their RL graphs.
4. Suspects {110, 145, 168}: Track A proper.

**Item-4 addition (HLO verification, next session):** record the topology
class of each HLO graph (simple/non-simple × tree/cyclic). Chordality says
none of {146, 180, 181} admits a simple forest — so if any HLO graph IS a
simple forest and verifies, that contradicts the theorem ⇒ implementation
bug somewhere ⇒ STOP and flag loudly before anything else.

**Policies (user directives, binding):**
1. Sparse Oracle Principle is the named finding (session-4 entry).
2. Anneal on suspects = Track A only; annealing failure is NEVER citable as
   evidence of non-realizability.
3. After next-session items 4–6 (HLO verify → oracle-treat → minimize):
   STOP and send the SPEC §8 email. The separator/HEI hunt does not start
   before the email is sent.

## 2026-06-12 — Session 4: published-graph oracles, the generator-gap proof, annealer

**Strategic update (user, supersedes the 6-orbit plan):** the mysteries were
resolved/attacked in He–Lee–Ooguri (arXiv:2601.19979, Jan 2026; code:
github.com/Jaeha0526/EntropyCone_RL): s ∈ {146, 180, 181} realized via RL;
s ∈ {110, 145, 168} resisted RL to 13 internal vertices (evidence, not proof,
of non-realizability). New plan next session: verify their three graphs in
the exact engine, oracle-treat their topologies, minimization pass; then race
(A) exact realization vs (B) separating-HEI hunt on {110, 145, 168}. The
repo's "6 open mysteries" framing is stale until item 7 of that plan lands.

**The 19 published C5 graphs transcribed and verified** (`hec/c5_graphs.py`,
`scripts/verify_c5_graphs.py`): 18/19 exact (entropy_vector == scale×ray;
scales 1–2). Verification caught real transcription traps: figures 10–13
arrived shuffled from a batched PDF read (adjudicated by matching each
edge list against all 19 rays); fig 18 has 16 edges (O has degree 3); fig
19's σ1–σ4 weight-2 edge passes visually *through* O (no σ1–O edge). Tools
that did the work: orbit-aware matching (one exact vector + 720 index
permutations), single/double-edit variant search, pool-subset search.
**Fig 12 still unresolved** (15 unit edges, congested center; exhaustive
pool search running). Trust nothing that passes near a vertex.

**NAMED FINDING — the Sparse Oracle Principle.** For LP cut-assignment
realization, search difficulty is governed by the topology's density, not
its coverage: a complete super-topology *contains* every realizing structure
(the LP could zero edges down to it) yet the weight-fit reliably fails
there, while on the exact sparse topology it converges in seconds. Evidence:
oracle-mode runs on the five testable holdout rays — published topologies,
weights stripped — recovered exact weights in 0–6 s (first to sixth
attempt), after cold search over dense super-topologies had failed for
hours. Mechanism: the number of candidate min-cut patterns per subset grows
with density, so the pin-assignment (outer combinatorial) search drowns;
sparsity collapses the pin space and the slack signal becomes informative.
Consequences: (i) realization search must walk *sparse structure space*
(hence `hec/anneal.py`, slack-guided topology moves); (ii) random sampling
of the sparse family is insufficient (ray 10's crown is a ~1e-7 draw);
(iii) at n=6 the same principle dictates annealing near the RL paper's
13-internal-vertex frontier rather than LP-on-dense-supergraphs.

**Topology annealer** (`hec/anneal.py`): local moves in the sparse-bulk
family (re-home/add/delete boundary straps, toggle bulk-bulk edges,
add/remove bulk vertices), fitness = best slack of a short fit_weights
probe, plus report mode in lp_realize. Cold results: rays 16, 17, 18
annealed (16: 15 edges scale 2; 17: 13 edges; 18: 16 edges) →
**16/19 rays realized fully independently**.

**19/19 certificates in reports/realizations/** — wait, 18/19 until fig 12
lands: rays 10 and 19 carry second-tier certificates (published topology
credited to arXiv:1903.09148, weights independently re-derived; engine field
says so). Ray 12's certificate needs the fig-12 transcription or an
annealing hit; the pool search continues in the background.

**Next:** the anneal-vs-LP lesson scales to n=6 — the same
slack-guided structure search is the realization branch for {110, 145, 168},
seeded near 13 internal vertices per the RL paper's frontier.

## 2026-06-12 — Session 3: LP realizer, Q3 campaign, HECATE goes public

**Project renamed HECATE** (Holographic Entropy Cone Analysis & Theorem
Engine) and published: https://github.com/c0mpli/hecate — public, MIT, main.

**LP cut-assignment realizer** (`hec/lp_realize.py`, the SPEC §6 engine v2):
two-phase per topology — slack-LP descent over re-pinned achieving cuts,
then, at zero slack, hard-equality constraint generation, which is a
*complete* decision procedure per (topology, pin assignment): pinned cuts
bound every entropy from above, so each LP round either matches the target
exactly or produces a violated cut as a new constraint row. Hits are
integerized (LCM of denominators) and verified against the exact engine
before being called real. Complete graphs on boundary + k bulk serve as
super-topologies — the min-Σw objective zeroes edges and discovers sparse
structure (it found the Bell-pair ray as literally one edge).

**C5 validation: 13/19 ray orbits independently realized** (certificates in
`reports/realizations/`, each with cyclomatic number for the T2/tree-
conjecture angle). The LP engine cracked rays 8, 11, 13, 14, 15 — all
unreachable by the v1 hill-climb (8/19). Notable: minimal-weight solutions
for 13/15 are *cyclic* two-hub graphs — minimum total weight does not favor
trees. Open: rays 10, 12, 16, 17, 18, 19 (logged at 300 attempts × seed 777,
~25 min each, no claim); they're structural cousins of cracked rays — next
steps are tree-DP cut enumeration and stabilizer-aware pin seeding rather
than more brute attempts.

**Q3 campaign result (honest ledger):**
- Weighted cube: contraction map INFEASIBLE (CP-SAT proof, session 2).
- Unit-expanded cube (L=16, R=18), copy-symmetric class model (8192 count
  classes) + anchor-distance domain tightening: CP-SAT **UNKNOWN** at the
  25-minute budget, twice. So Q3 — alone among the eight 5-party orbit
  representatives — resists naive mechanical proof: exactly the regime the
  deterministic algorithm of arXiv:2403.13283 was built for. Implementing it
  is the designed next prover milestone; machinery for the symmetric
  expanded search (`find_contraction_symmetric_expanded` + independent
  checker + full-cube edge sweep) is in place and reusable for the many
  non-unit-coefficient 6-party HEIs.

**P3 chain closed:** computed HEI-violator index set == the paper's
published 52-element s-list (`verify_er6.py`), which also proves the data
repo's row order matches the paper's labels — the mystery-target extraction
now rests on verification, not assumption.

**Paper context for T1** (§5.3 of 2412.15364): the authors note the 6
mystery orbits may need much more complex graphs OR may violate a yet-
unknown 6-party HEI — and "it is tempting to speculate that they are indeed
holographic" (every known non-holographic ER at n=6 violates an n≤5 HEI).
Both attack directions are live: realization (T1+) and new-facet hunting
that kills a mystery orbit (T1−/T3 combined — the bigger result if true).

**Mystery pass with the LP engine:** no realization for any of the 6 orbits
(80 LP attempts each, ~4.5 min/orbit, seed 4242) — logged in
`reports/mystery_attempts.jsonl`, no claims. Sustained T1 campaign design:
(i) exhaustive small-tree topology sweeps with per-(topology, assignment)
infeasibility certificates — the publishable-exclusion path; (ii) the
new-6-party-HEI hunt (T3) which could classify a mystery orbit negatively.

**Repo hygiene (pre-outreach):** build/ artifact purged from git; CI
(GitHub Actions, pytest on push) + badge; Data & references section pinning
the Rota data at commit e973df6e0aa6 (fetch script clones that snapshot);
CITATION.cff; MIT license; v0.1.0 release.

## 2026-06-12 — Session 2: M1 + M2 complete, P2 + P3 reproduced, M3 scaffolded

**M1 acceptance.** `verify_engine.py`: 1,000,000 random graphs (igraph fast
path, 6 workers), zero SA/AL/SSA/WM/MMI violations, 39.8 s. Fast path is
exact for integer weights (sums ≪ 2⁵³) and cross-validated against the
networkx reference on 360 graphs at n=3,4,5.

**P2 — the 5-party cone (arXiv:1903.09148), reproduced exactly** from
transcribed Tables 1–2 (`verify_c5.py`):
- 8 inequality orbits expand under purified Sym(6) to exactly the paper's
  sizes (15,20,45,72,10,60,60,90) → 372 facet instances.
- All 19 ray representatives satisfy all 372 instances and are extreme
  (saturated-facet rank 30 = dim−1, exact sympy).
- 19 distinct orbits, sizes summing to exactly 2267.
- `--duality`: Normaliz (exact double description, 19 min) re-derives the
  ray set from the 372 facets — equals the 19-orbit expansion **exactly**.

**M2 — contraction-map prover** (`prove_inequalities.py`, certificates in
`reports/contraction_maps/`):
- MMI re-derived by brute force in 0.5 s (the P1 deliverable); CP-SAT agrees.
- CP-SAT proves MMI2, QCyclic, Q2, Q4, Q5 (full all-pairs verification).
- Q3: CP-SAT returns INFEASIBLE on the *weighted* cube — a small theorem:
  Q3 has no weighted-cube contraction map; its proof needs the unit-expanded
  cube (3·S(ABC) → three coordinates), i.e. exactly the hard case that
  motivated the deterministic algorithm of arXiv:2403.13283. Next prover
  milestone: unit expansion (+ symmetry reduction over repeated coordinates).
- Canonicalization (`canon.py`): Sym(n+1) lex-min vector keys; weighted-graph
  keys via pynauty (edge-subdivision encoding, boundary vertices pinned).

**P3 — He–Hubeny–Rota classification (arXiv:2412.15364), re-verified from
scratch** (`verify_er6.py`, 208 rays from the paper's GitHub data repo,
mirrored in `data/raw/rota/`):
- All 208 are extreme rays of the 6-party subadditivity cone (saturated-SA
  rank 62; the SAC needs ALL polychromatic SA instances — 903 of them — not
  just the 21 atomic ones; bug caught by rank ceiling at 21) and all are
  SSA-compatible (3003 instances).
- HEI classification: checking all Sym(7) images (5040 index-permutations,
  numpy) against the 1877 Czech et al. orbit representatives gives exactly
  **52 violators / 156 clean — matching the paper**. (Representatives alone
  give 30 — orbit expansion is essential.)
- The 6 mystery orbits s ∈ {110, 145, 146, 168, 180, 181} confirmed clean →
  written with provenance to `data/targets/mystery_orbits.json`. These are
  the T1 targets.

**M3 scaffold** (`realize.py` v1: hill-climb over tree-biased topologies +
star/double-star motifs, integer weights, exact double verification):
- Independently realized 8/19 five-party orbits (all 7 star rays + ray 9)
  with certificates in `reports/realizations/` — found without looking at
  the paper's published graphs.
- Bounded first pass on the 6 mystery orbits (200 restarts × 3000 moves
  each): no realization — logged in `reports/mystery_attempts.jsonl`, no
  claim implied. The real attack is the (topology, cut-assignment) → LP
  feasibility engine of SPEC.md §6, which also yields exclusion certificates.

**Corrections to SPEC.md numbers:** Czech ancillary has **1877** inequalities
(not 1876); the data lives in M. Rota's GitHub repo (Zenodo DOI
10.5281/zenodo.14983856) — the arXiv v3 source tarball has no anc/ files.

**Next session:** LP cut-assignment realizer (trees first, per the tree
conjecture); unit-expanded Q3 proof; parse the 19 published C5 graphs
(data/raw/1903.09148/01..19.pdf) to cross-check the realizer; then sustained
mystery-orbit runs with exclusion bookkeeping.

## 2026-06-12 — Day 1: engine built and verified

**Done (full Day-1 checklist from SPEC.md):**

- All 9 reading-list papers fetched (`scripts/fetch_papers.sh`), plus ancillary
  data. The spec's arXiv IDs and claims all check out — the He–Hubeny–Rota
  abstract confirms: 208 genuine 6-party orbits, 52 non-holographic, 150
  realized by graphs (148 trees, 2 with a bulk cycle), **6 "mystery" orbits
  open**. Those 6 are the T1 targets.
- `entropy_vector(G, n)`: graph → S-vector via min-cut (networkx, super-
  source/sink reduction, uncapacitated edges = infinite). Integer weights
  throughout ⇒ every entropy exact.
- `check_vector(S, n)`: all SA / AL / SSA / WM / MMI instances over disjoint
  party subsets.
- Hand-computed ground truth (M0 acceptance): star graphs with bulk center
  (`S(A)=min(a, b+c+o)` etc.) and an all-boundary 4-cycle that *saturates*
  MMI (20 = 20). Both match the engine — `tests/test_entropy.py`.
- **The Day-1 assertion: 10,000 random graphs (stars / random trees with 0–4
  bulk vertices / trees + extra edges ⇒ bulk cycles), integer weights, seed
  2026 → zero violations of any inequality, exact arithmetic, 15.9 s.**
  Bonus: 500 graphs at n=4 and 200 at n=5 — also zero violations.
  Reproduce: `.venv/bin/python scripts/day1_mmi.py --count 10000 --seed 2026`

**Why the assertion *must* pass (checklist item 5):** for min-cut entropies,
MMI has a proof by cut-and-paste: given the minimal cuts for AB, AC, BC, their
union-and-intersection rearrangement produces candidate cuts for A, B, C, ABC
whose total weight is no larger (each edge is counted at least as many times
on the left as the right). Quantum states have no such mechanism — entropy of
a generic state is not a min-cut of anything. Live demo of the asymmetry:

```
>>> ghz = {m: 1 for m in range(1, 8)}   # 4-qubit GHZ: every bipartition has S=1
>>> check_vector(ghz, 3)
[('MMI', 1, 2, 4, -1)]                  # S(AB)+S(AC)+S(BC)=3 < 4=S(A)+S(B)+S(C)+S(ABC)
```

GHZ entanglement is quantum-legal but **cannot be geometry** — no weighted
graph, hence no smooth spacetime region, ever produces that vector. The HEC
facets are exactly these laws separating geometric from merely-quantum
entanglement. Day 1 verified one of them (MMI) from both sides.

**Data inventory:**

- `data/raw/2309.06296/anc/HEIforms.txt` + `HEIvectors.txt` — 1,876 known
  holographic entropy inequalities; vectors are 63 tab-separated integer
  coefficients per line (n=6 subset ordering to be confirmed against the
  paper), forms are Mathematica-style subset lists. P3 input.
- `data/raw/2412.15364/` — paper source only; **no machine-readable ancillary
  files**. The 208 orbit S-vectors (and the 6 mystery orbits) are in the .tex
  tables/figures — extraction + cross-check against the paper is a P3 task.

**Environment** (macOS, uv-managed CPython 3.12 in `.venv`): networkx 3.6.1,
python-igraph 1.0.0, numpy 2.4.6, sympy 1.14.0, ortools, pycddlib 3.0.2
(needs `brew install cddlib gmp`), pynauty 2.8.8.1 (needs `brew install
nauty`, build with `CFLAGS="-I$(brew --prefix)/include -I$(brew --prefix)/include/nauty"`),
Normaliz 3.11.1 (no brew formula — official binary unzipped to
`~/.local/opt/normaliz-3.11.1`, symlinked into `~/.local/bin`).

**Next (M0→M1):** read N&C ch. 2 + Preskill ch. 10 alongside BNOSSW §2–3;
then the igraph fast path + 10⁶-graph run, and encode the 19 five-party
extreme-ray orbits from arXiv:1903.09148 in exact arithmetic.

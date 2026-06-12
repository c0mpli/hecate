# Lab notebook

Newest entries first. Every claim here must be reproducible from a command in
this repo.

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

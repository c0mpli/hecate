# Holographic Entropy Cone — Contribution Spec
**For:** Jash · **Goal:** a genuine, emailable research contribution in 6–12 months of part-time work (~8 hrs/week)
**Field status verified:** June 2026

---

## 0. Mission in one paragraph

The holographic entropy cone (HEC) is the program that maps *exactly which patterns of entanglement are capable of being geometry*. Every facet of this cone is a candidate law constraining how spacetime can emerge from entanglement — your "problem #6" in miniature. The cone is fully solved for 5 regions, **partially open for 6**, and almost untouched beyond. The math is combinatorial (graphs, min-cuts, polyhedra, SAT-style search), the verifiers are fast and exact, and the active groups are small. This is the rare place where an ML/systems engineer can reach a real open problem in quantum gravity without first learning GR, QFT, or string theory.

---

## 1. The problem, precisely

- **Setup:** Split a quantum system into `n` named parts A₁…Aₙ plus a purifier O. For every nonempty subset I of the parts, compute its entanglement entropy S(I). Stack these into an **entropy vector** S ∈ ℝ^(2ⁿ−1). For n=6 that's a 63-dimensional vector.
- **The cone:** The set of entropy vectors achievable by *holographic* states (states with a smooth geometric dual via the Ryu–Takayanagi formula) forms a **closed, convex, polyhedral, rational cone** — the HEC. Describe it either by its **facets** (entropy inequalities) or its **extreme rays** (the "atomic" entanglement patterns that generate everything else).
- **The miracle that makes this computable (BNOSSW 2015):** an entropy vector is holographic **iff** it is realizable by a weighted graph: boundary vertices = the n parts + purifier, any bulk vertices, non-negative edge weights, and
  `S(I) = weight of the minimum cut separating boundary vertices in I from the rest of the boundary.`
  Geometry → graphs → max-flow/min-cut. The entire field reduces to graph combinatorics + polyhedral geometry.
- **The two verifiers (this is why AI-style search works here):**
  1. *Is vector v holographic?* Exhibit a graph realizing it. Checking a graph = 2ⁿ−1 min-cut computations (63 for n=6, microseconds).
  2. *Is inequality Q valid on all holographic states?* Exhibit a **contraction map** (a discrete 1-Lipschitz map between hypercube subsets defined by Q). Checking a map is mechanical; finding one is a finite combinatorial search. Completeness of this proof method for rational inequalities was proven in 2025 (arXiv:2506.18086) — so contraction maps are not just sufficient, they're the whole game.

**Known structure:**
| n | Status |
|---|--------|
| 2–3 | Solved. Facets: subadditivity + **MMI** (monogamy of mutual information). |
| 4 | Solved — no genuinely new inequalities beyond instances of the above. |
| 5 | Solved. 19 extreme-ray orbits; cone completed by Hernández Cuenca 2019 (arXiv:1903.09148). |
| 6 | **OPEN.** See §2. |
| ≥7 | Wide open except a couple of known infinite families (cyclic, toric-type). |

---

## 2. State of the art & the contribution menu (verified June 2026)

Key recent results that define the frontier:

1. **He–Hubeny–Rota, Dec 2024 (arXiv:2412.15364)** — computed all SSA-compatible extreme rays of the 6-party subadditivity cone. Found **208 genuinely-6-party orbits**: 52 violate known holographic inequalities (so: not holographic), 156 don't. They constructed holographic graph models for **150 of the 156**.
   → **SIX ORBITS REMAIN UNRESOLVED: nobody knows if they are holographic.**
   → Of the 150 realized, 148 graphs are trees; **2 contain a bulk cycle**, leaving open whether tree-equivalent models exist (this bears on the "tree conjecture" from arXiv:2204.00075).
2. **Czech et al. 2023 (arXiv:2309.06296)** — large harvest of new 6-party holographic entropy inequalities, with **public ancillary data files** (all known facets + extreme rays). Completeness of the 6-party facet list: unknown.
3. **Bao–Naskar 2024 (arXiv:2403.13283)** — deterministic algorithm for finding contraction maps; exponential speedup over old greedy search; handles inequalities the greedy method couldn't.
4. **Bao–Furuya–Naskar 2024–25 (arXiv:2409.17317, 2506.18086)** — reframed "find all inequalities" as "enumerate all partial-cube image graphs," and proved completeness of the contraction-map method. Note: Naskar's affiliation includes the NSF AI Institute for AI & Fundamental Interactions — the AI-for-this-exact-problem angle is institutionally live but young.

### Ranked contribution targets

- **T1 (primary): resolve any of the 6 open orbits.** Either find a graph realizing one (instant co-author-grade result; verifier = 63 min-cuts) or build strong impossibility evidence (e.g., exhaustive exclusion over all graphs up to k bulk vertices — a negative result with a certificate is also publishable).
- **T2: the 2 bulk-cycle graphs** — find tree-topology equivalents, or push evidence that none exist. Directly attacks a named conjecture.
- **T3: new 6-party facet hunting** — generate candidate inequalities (via partial-cube enumeration or evolutionary search), prove via contraction maps, check novelty/independence against the Czech et al. data.
- **T4: ray hunting** — random/evolutionary graph generation, keep anything whose entropy vector falls outside the cone of currently known rays (LP check). Every hit is automatically holographic (it came from a graph) ⇒ new extreme-ray candidate.
- **T5 (tooling, guaranteed value): a fast, open-source, parallel HEC toolkit** — entropy engine + exact cone tools + the 2403.13283 deterministic prover, properly engineered. The field runs on one-off academic scripts; a maintained library gets used and cited.

T1/T2 are narrow, concrete, and time-boxed — start there. T3/T4 are the open-ended FunSearch-shaped hunts. T5 happens automatically as you build.

---

## 3. Prerequisites — in order, with time estimates

You do **NOT** need: general relativity, quantum field theory, string theory, or AdS/CFT machinery. Light holography literacy comes later, only for writing intros and talking to physicists.

| # | Topic | Source | Time @ ~8h/wk |
|---|-------|--------|----------------|
| 1 | Density matrices, partial trace, purification | Nielsen & Chuang §2.4–2.5 | 1 week |
| 2 | Von Neumann entropy, mutual information, subadditivity, SSA | Nielsen & Chuang ch. 11 + Preskill lecture notes ch. 10 | 1–2 weeks |
| 3 | Polyhedral cones: extreme rays, facets, Farkas/LP duality, double description | Ziegler *Lectures on Polytopes* ch. 0–2, or any LP text; install & play with Normaliz | 3–5 days |
| 4 | Max-flow / min-cut | You know this. Refresh multi-terminal → s-t reduction. | 1 day |
| 5 | RT formula *conceptually* | Van Raamsdonk's essay "Building up spacetime with quantum entanglement" (arXiv:1005.3035) + intro of Rangamani–Takayanagi review | 1 week (parallel) |
| 6 | The graph model + contraction maps | The 2015 paper itself (§2–3 of arXiv:1505.07839) is the real textbook | absorbed during M1–M2 |

Total runway before real coding: **~3–4 weeks.** Items 4–5 can overlap with 1–3.

---

## 4. Papers to reproduce (in order) — with deliverables

**P1. Bao–Nezami–Ooguri–Stoica–Sully–Walter 2015, "The Holographic Entropy Cone" (arXiv:1505.07839)**
Reproduce:
- Graph → entropy-vector engine (min-cuts over all 2ⁿ−1 subsets).
- Verify subadditivity, SSA, and MMI hold on ≥10⁶ random weighted graphs (zero violations expected — this is your engine's unit test).
- Implement the contraction-map *checker*, then re-derive the MMI proof by finding its contraction map yourself.

**P2. Hernández Cuenca 2019, "The holographic entropy cone for five regions" (arXiv:1903.09148)**
Reproduce:
- Encode the 19 extreme-ray orbits; verify each published graph yields its claimed ray (exact rational arithmetic).
- Verify facet↔ray duality of the 5-party cone with Normaliz/cdd (double description).

**P3. He–Hubeny–Rota 2024 (arXiv:2412.15364) + data from Czech et al. (arXiv:2309.06296)**
Reproduce:
- Load their ancillary data (rays, inequalities). Re-verify the classification of the 208 orbits against known inequalities with your own code.
- Extract the **6 unresolved orbit vectors** → these are your T1 targets.

**Method paper to implement (not reproduce end-to-end): Bao–Naskar 2024 (arXiv:2403.13283)** — the deterministic contraction-map algorithm becomes your `prover` module.

Reproduction is not busywork: it calibrates your code against ground truth, and mismatches you find are themselves worth reporting.

---

## 5. Software architecture

Language: Python (+ Rust/C++ hot paths later if needed). No quantum hardware, no GPU required — this is CPU combinatorics, embarrassingly parallel.

```
hec/
├── graphs.py       # generation (random, tree-biased, mutation ops), pynauty canonical labeling
├── entropy.py      # S-vector via min-cut: merge I → super-source, rest of boundary → super-sink
│                   # float path (igraph/networkx) for search; exact Fraction path for claims
├── cone.py         # LP membership (scipy/CVXPY float → sympy/pycddlib exact),
│                   # dual separating-hyperplane certificates, Normaliz bindings,
│                   # Sym(n+1) orbit canonicalization of rays & inequalities
├── prover.py       # contraction maps: deterministic rules of 2403.13283 + CP-SAT (OR-Tools) fallback
├── realize.py      # T1/T2 engine: target ray → search over (topology, cut-assignment) →
│                   # per-assignment LP feasibility on weights (see §6)
├── falsify.py      # counterexample search for candidate inequalities (weight optimization per topology)
├── search.py       # evolutionary loop; optional LLM-proposer (FunSearch pattern)
├── db.py           # dedupe store keyed by canonical forms; provenance for every claim
└── reports/        # auto-generated certificates: graph + exact S-vector + LP/contraction proof
```

**Non-negotiable engineering rules**
1. **Exact arithmetic for any claim.** Floats find candidates; `fractions.Fraction`/sympy verify them. A "discovery" with float roundoff is a retraction waiting to happen.
2. **Canonicalize everything.** The symmetry group Sym(n+1) (parties + purifier, 5040 elements for n=6) plus graph isomorphism will otherwise drown you in duplicates. Use nauty canonical forms; store orbit representatives only.
3. **Every result ships with a machine-checkable certificate** (the graph, its exact entropy vector, the LP/contraction witness). This is what makes a physicist trust an outsider's email.

---

## 6. Search-loop design

**T1 — Realizing a target ray r (the 6 open orbits):**
For a *fixed* graph topology, S(I) = min over cuts of a linear function of edge weights. So:
- Choose a **cut assignment**: for each of the 63 subsets I, pick which cut achieves the minimum.
- That choice turns realization into an **LP feasibility problem**: chosen cuts have weight-sum = r_I (up to one global scale), all other cuts ≥ r_I.
- Outer loop searches (topology, cut-assignment) pairs — CP-SAT or guided enumeration, trees first (148/150 known models are trees), small bulk-vertex counts first.
- Negative results compound: "no realization with ≤ k bulk vertices" is a logged, certifiable exclusion. Push k as far as compute allows.

**T4 — Ray hunting (open-ended):**
```
loop:
  g ← generate/mutate graph          # tree-biased priors
  v ← entropy(g)                     # float
  if LP says v ∉ cone(known_rays):   # separating hyperplane = score
      verify exactly; canonicalize; if new → DB + alert
  evolve population on score = violation margin − size penalty
```

**T3 — Inequality hunting:** generate candidates (partial-cube enumeration per 2409.17317, or evolve integer coefficient vectors that hold on all known rays) → prover attempts contraction map → falsifier attempts counterexample graph → survivors checked for independence from known facets (LP duality) → novelty check vs. Czech et al. data.

**FunSearch layer (optional, after the plain loop works):** an LLM proposes *generator programs* (Python functions emitting graph families or inequality families); the verifier stack scores them; evolve the program population. Don't start here — start with dumb evolutionary search + perfect verifiers. The verifiers are the product; the proposer is swappable.

**Compute:** your laptop for M1–M2; one 32–64 core box (or spot instances) for the hunts. Budget: trivial by your ML standards.

---

## 7. Milestones & acceptance criteria

| Milestone | Window | Acceptance test |
|-----------|--------|-----------------|
| **M0** Prereqs + env | wk 1–4 | Can hand-compute S-vectors for 3-party star graphs; Normaliz installed and understood |
| **M1** Entropy engine + cone tools | wk 4–8 | 10⁶ random graphs, zero SA/SSA/MMI violations; all 19 five-party orbits reproduced in exact arithmetic |
| **M2** Prover + canonicalization | wk 8–14 | Contraction maps found mechanically for MMI + ≥1 five-party inequality; dedupe DB live |
| **M3** The hunt | mo 4–6 | T1 search running at scale on the 6 open orbits; T4 loop live; exclusion certificates accumulating |
| **M4** Result + write-up | mo 6–9 | One of: realization found / strong impossibility evidence / new ray / new proven facet / toolkit + reproduction report. Email sent (see §8) |
| **M5** Paper or collaboration | mo 9–12 | arXiv note (solo or with the group that adopts you) |

Every M4 branch is a win — including the toolkit branch. "I reproduced your results, here's a 100× faster open library, and here's my exclusion data on the 6 orbits" is a door-opening email even with zero new theorems.

---

## 8. Community & contact protocol

**Who (the active groups):**
- Veronika Hubeny & Massimiliano Rota (UC Davis QMAP) + Temple He (Caltech) — the 6-party/extreme-ray program. Your T1/T2 results go here first.
- Ning Bao (Northeastern/Brookhaven) & Joydeep Naskar — contraction-map algorithmics; most receptive to the AI/automation angle.
- Bartek Czech (Tsinghua) & Sergio Hernández Cuenca — inequality families, data repository.

**When:** only after M2 — i.e., with reproduction receipts in hand. Never before.

**The email (5 lines, this exact shape):**
1. "I reproduced [specific result] from your paper [arXiv:xxxx] — code here [repo]."
2. "I built [tool] and ran [search] at [scale]."
3. "Found: [concrete artifact + attached certificate]."
4. One precise question about *their* stated open problem.
5. Full stop. No life story, no theory-of-everything talk.

---

## 9. Risk register & kill criteria

| Risk | Reality check | Mitigation |
|------|---------------|------------|
| Scooped on the 6 orbits | Active groups exist; could happen any month | Speed on T1; T5 toolkit retains value regardless; T3/T4 are effectively inexhaustible |
| The 6 orbits are open *because they're hard* | Likely true | Exclusion certificates are publishable partial progress; pivot weight to T3/T4 |
| Float-arithmetic false discovery | Classic outsider failure | Rule #1 in §5 — exact verification before any claim |
| Drowning in math beyond plan | QI entropies may take longer than 2 wks | Time-box prereqs to 6 wks max; if still stuck, switch entry problem (QECC search) before quitting |
| **Displacing BlippAI / SmartLens / Niksla** | The real risk for you specifically | Hard cap: 8 hrs/wk, weekends only. **Pause trigger:** if BlippAI closes and onboarding load spikes, park at the nearest milestone, push the repo public, leave a NOTES.md. The project keeps; the cone isn't going anywhere. |

This is a marathon side-quest. The failure mode isn't "too dumb" — it's "sprinted for 6 weeks, burned out, quit before M2." Boring consistency wins.

---

## 10. Reading list (in consumption order)

1. Nielsen & Chuang, ch. 2 + 11 (the only textbook chapters you need)
2. Preskill lecture notes, ch. 10 (entropy) — free online
3. Van Raamsdonk, arXiv:1005.3035 (the "spacetime from entanglement" essay — your motivation anchor)
4. **arXiv:1505.07839** — BNOSSW, the founding paper (read §2–3 five times)
5. **arXiv:1903.09148** — 5-party solution
6. **arXiv:2412.15364** — the N=6 frontier + your targets (grab ancillary files)
7. arXiv:2309.06296 — inequality harvest + data repository
8. arXiv:2403.13283 → 2409.17317 → 2506.18086 — the contraction-map algorithmics arc
9. arXiv:2204.00075 — marginal independence + the tree conjecture (context for T2)

---

## Day-1 checklist (first weekend)

- [ ] Download papers 4–8 above + ancillary data files from arXiv
- [ ] Repo init; install networkx/igraph, sympy, OR-Tools, pycddlib, pynauty, Normaliz
- [ ] Implement `entropy(graph) → S-vector` for n=3 via min-cut
- [ ] Generate 10,000 random weighted graphs; assert MMI holds on all
- [ ] Watch the assertion pass and understand *why* it must: you have just verified, on your own machine, a law of quantum gravity that ordinary quantum states are free to violate. That asymmetry — what geometry permits vs. what quantum mechanics permits — is the entire field.

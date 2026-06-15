# Attack on s=207 — the unexplored bulk-cycle twin of s=111

s=111 and s=207 are the two **bulk-cycle** orbits of arXiv:2412.15364 whose tree-realizability is the open question. s=207 was untouched for one reason: no starting realization (seed). This was the whole blocker, so STEP 0 was to get one.

Reproduce: `.venv/bin/python -m hec.attack_207`. Exact Fraction arithmetic; bounded negatives only.

## STEP 0 — seed obtained (the blocker, resolved)

- **Source:** arXiv:2412.15364 (He-Hubeny-Rota) figure ER_graphs.pdf, entry #207, the 'simple graph' column (one boundary vertex per party).
- **Verification:** transcribed from the figure, Sym(7) orbit-matched to our representative, and EXACT-verified (Fraction) to realize 2x the s=207 representative; perm from the paper's labels to ours is the identity.
- **hecdata:** 207 is ABSENT from the hecdata graph repo (github.com/SergioHC95/Holographic-Entropy-Cone, 4145 n=6 graphs scanned, no orbit match).
- **LP construction:** lp_realize_target found no realization in 24 tries / ~550 s (the same bottleneck that blocked 111).

So the figure transcription (exact-verified — the s181 lesson: a misread edge would not match the ray) is what unblocked 207.

## STEP 1 — the seed is genuinely the bulk-cycle case

- seed realizes **2×** the s=207 representative (exact, all 63 components).
- SA+SSA: True; SAC-extreme (saturated-SA rank 62 = 62): True; HEI-clean: True; non-chordal: True (expected — a surviving bulk cycle).

- **structure:** cyclomatic 4 = a pure-bulk 4-cycle (vertex degrees [4, 4, 5, 5]) + 3 removable boundary triangles. The pure-bulk cycle is the hard core: no triangle, no degree-3 bulk vertex, so the local entropy-preserving moves cannot touch it.

## STEP 2 — tree-finding (cycle_surgery)

BOUNDED: no entropy-preserving move sequence reduced s=207's realization to a tree under the complete local move set (frontier emptied at 127 canonical states, best cyclomatic 1). NOT a proof no tree exists; 207 IS holographic.

## s=111 vs s=207

| | seed cyclomatic | pure-bulk core | surgery | best cyclomatic |
|---|---|---|---|---|
| s=111 | 3 | 4-cycle deg [4, 4, 4, 5] | no_reduction | 1 |
| s=207 | 4 | 4-cycle deg [4, 4, 5, 5] | no_reduction | 1 |

**Same obstruction class: True.** Both twins reduce (under the complete local move set) to a surviving PURE-BULK cycle and neither reaches a tree -> the bulk-cycle obstruction is a GENERAL phenomenon shared by 111 and 207, not specific to 111. 207's seed carries 3 extra REMOVABLE boundary triangles (cyclomatic 4 vs 111's 3), but its irreducible core is the same pure-bulk 4-cycle with degree-4/5 vertices.

## Honesty

- Bounded negative only: *no tree found under {this move set, this seed, this bound}* — never "no tree exists". s=207 IS holographic (it is realized, with a bulk cycle); only the tree question is open.
- The seed is exact-verified before any downstream use.
- A possible next lever (not run here): 207's surgery frontier bottoms out on an all-degree-3 pure-bulk cycle, where Y→Δ is nominally applicable — a wider/deeper or fine-graining search could be tried, exactly as for 111.
- Suspects {110,145,168}, the email, the README, and s=111's committed seed are untouched.

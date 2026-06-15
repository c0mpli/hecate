# Obstruction search — is s=111 structurally special or just hard?

A **cheap, LP-free** test (no weight fitting, no realization search). Instead of searching for a tree realization of the bulk-cycle orbit `s=111`, we look for a vector/structural **invariant** that separates it from every ray *known* to be tree-realizable. A separator (that also passes the control) would be a candidate obstruction — a reason, not an absence. No separator means 111 looks ordinary, i.e. merely hard to crack.

Reproduce: `.venv/bin/python -m hec.obstruction_search`. All values exact (integer / graph-structural).

## Reference set & the control

- **Tree-realizable reference set:** the 148 tree-realized n=6 orbits of arXiv:2412.15364 + all 19 n=5 orbits of arXiv:1903.09148 (every C5 orbit is tree-realizable).

- **Chordality census of the 148 n=6 trees:** 44 chordal (simple-tree) + **104 NON-chordal** (non-simple-tree). So chordality detects *“has a bulk cycle”*, **not** non-realizability — it flags 104 confirmed tree-realizable rays and both controls. It is the canonical trap, and the real comparison cohort is these 104 non-chordal-but-tree-realizable rays.

- **Controls (critical):** C5 rays **10** and **17** are tree-realizable (non-simple) yet non-chordal — the n=5 analogue of 111. An obstruction must NOT flag them.

- **Targets:** `s=111` (primary) and `s=207`, the two bulk-cycle orbits.

## Invariant table

`agn` = value comparable across n; `deg` = constant across cohort (no signal); `out?` = target strictly outside cohort range; `ctl` = controls 10/17 inside (n-agnostic keys only). Percentile is within the 104-ray same-n (n=6) cohort.

| invariant | agn | deg | cohort min..max (mean) | s=111 (pct) | out | s=207 (pct) | out | c5:10 | c5:17 | ctl |
|---|---|---|---|---|---|---|---|---|---|---|
| `chordal` | Y | · | 0..0 (0.0000) | 0 (100.0) |  | 0 (100.0) |  | 0 | 0 | yes |
| `n_hyperedges` |  |  | 41..58 (53.5096) | 54 (59.6) |  | 57 (92.3) |  | 28 | 30 |  |
| `lg_density` | Y |  | 0.9899..0.9988 (0.9965) | 0.9972 (53.8) |  | 0.9912 (0.0) |  | 0.9921 | 0.9931 | yes |
| `lg_clique_number` |  |  | 39..56 (50.4423) | 50 (43.3) |  | 50 (43.3) |  | 25 | 27 |  |
| `lg_num_max_cliques` |  |  | 4..64 (9.5577) | 16 (91.3) |  | 29 (97.1) |  | 8 | 8 |  |
| `lg_cyclomatic` |  |  | 778..1594 (1353.7308) | 1374 (46.2) |  | 1526 (79.8) |  | 348 | 403 |  |
| `lg_deg_max` |  |  | 40..57 (52.5096) | 53 (59.6) |  | 56 (92.3) |  | 27 | 29 |  |
| `lg_deg_min` |  |  | 39..56 (50.6923) | 52 (67.3) |  | 53 (73.1) |  | 26 | 28 |  |
| `shortest_hole` | Y | · | 4..4 (4.0000) | 4 (100.0) |  | 4 (100.0) |  | 4 | 4 | yes |
| `n_4holes` |  |  | 1..40 (6.1250) | 6 (66.3) |  | 42 (100.0) | **\*** | 3 | 3 |  |
| `holes_per_hyp` | Y |  | 0.0172..0.7143 (0.1187) | 0.1111 (64.4) |  | 0.7368 (100.0) | **\*** | 0.1071 | 0.1000 | yes |
| `core_nodes` |  |  | 41..58 (53.5096) | 54 (59.6) |  | 57 (92.3) |  | 28 | 30 |  |
| `n_distinct_values` |  |  | 3..9 (6.7885) | 6 (38.5) |  | 3 (1.9) |  | 3 | 6 |  |
| `max_value` | Y |  | 3..10 (6.9912) | 6 (38.5) |  | 3 (1.9) |  | 3 | 7 | yes |
| `purifier_S` |  |  | 1..4 (2.8173) | 2 (26.9) |  | 1 (1.9) |  | 1 | 3 |  |
| `sa_saturated` |  |  | 123..223 (167.6058) | 164 (39.4) |  | 119 (0.0) | **\*** | 57 | 49 |  |
| `ssa_saturated` |  |  | 300..695 (448.3942) | 419 (36.5) |  | 301 (1.0) |  | 102 | 91 |  |
| `mmi_saturated` |  |  | 26..33 (29.7500) | 31 (83.7) |  | 28 (26.9) |  | 14 | 11 |  |
| `mmi_sat_frac` | Y |  | 0.5000..0.9429 (0.8263) | 0.8857 (83.7) |  | 0.8000 (26.9) |  | 0.7000 | 0.5500 | yes |
| `mmi_min_slack` |  | · | 0..0 (0.0000) | 0 (100.0) |  | 0 (100.0) |  | 0 | 0 |  |
| `zero_pair_MI` |  | · | 21..21 (21.0000) | 21 (100.0) |  | 21 (100.0) |  | 15 | 15 |  |
| `independent_parties` | Y |  | 6..7 (6.9123) | 7 (100.0) |  | 7 (100.0) |  | 6 | 6 | yes |

## Verdict

**s=111 (primary): no separator.** No non-degenerate invariant in this battery puts 111 outside the non-chordal tree-realizable cohort (including the 10/17 controls). Across the 17 discriminating invariants it sits at percentiles **26.9–91.3** of the 104 same-n tree-realizable rays — strictly interior, usually near the median, never at an edge. **Evidence that s=111 is an ordinary tree-realizable ray that is merely hard to crack, not a structural counterexample to the strong tree conjecture.** This is *not* a proof of realizability (111 IS holographic; only the tree question is open); it redirects effort to the search filter rather than to a non-existence claim.

**s=207 (secondary): marginal only.** 207 lies just outside the cohort on `n_4holes, holes_per_hyp, sa_saturated` — small boundary excursions on count-type invariants (42 vs max 40 holes; 0.737 vs 0.714 hole density; 119 vs min 123 SA-saturated). The cohort edge is itself a tree-realizable ray, so this is the high-density END of a continuum, not a clean gap — weak, single-boundary, and 207 has no studied cyclic seed. Not a candidate obstruction in the strong sense; it does show the test is not trivially returning “inside”.

## Honesty

- “No separator” means none in *this* battery of cheap invariants, not that none can exist.
- A differing/equal invariant value is correlation, never proof; no non-realizability is claimed from any invariant.
- s=111 and s=207 ARE holographic (each realized, with a bulk cycle); only tree-vs-cycle is open.
- Suspects {110,145,168} are not analyzed here.

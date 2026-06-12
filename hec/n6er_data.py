"""The two explicitly-published tree-resistant N=6 models (arXiv:2204.00075,
figs. N6er1/N6er3) — transcribed and exactly verified (SA+SSA hold; both
contain a pure-bulk 4-cycle).

Cross-reference findings (session 5): neither vector is among the 208
SSA-compatible SAC6-extreme orbits — saturated-SA ranks are 58 (N6er1) and
61 (N6er3), i.e. their PMIs are higher-dimensional SAC faces. They are HEC6
extreme rays of a different stratum; no overlap with suspects {110,145,168}.

N6er3 is special: 2204.00075 explicitly reports failing to find a tree model
for it ("we have not found a tree form"). A verified tree realization of
N6ER3_VECTOR would resolve an open item of that paper — prime
party-splitting-annealer target after rung 1.
"""

A, B, C, D, E, F, O = 0, 1, 2, 3, 4, 5, "O"

N6ER1_EDGES = [
    (A, "b3", 2), (F, "b2", 2), (E, "b2", 2), (D, "b4", 2), ("b3", "b2", 1),
    ("b3", C, 1), ("b3", "b1", 1), ("b3", B, 1), (C, "b1", 1), ("b1", O, 1),
    (O, "b2", 2), ("b1", "b4", 1), (O, "b4", 1), (B, "b4", 1), ("b2", "b4", 1),
]

N6ER3_EDGES = [
    (F, "b1", 1), (F, "b4", 1), (A, "b1", 1), ("b1", "b4", 1), ("b4", D, 1),
    (D, "b3", 1), ("b4", "b3", 1), ("b3", B, 2), ("b4", O, 2), (O, "b2", 1),
    ("b1", "b2", 1), ("b2", "b3", 1), ("b2", C, 1), (C, "b3", 1), ("b2", E, 2),
]

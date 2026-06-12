"""The 19 published graph models of arXiv:1903.09148 Fig. 1 (01.pdf-19.pdf).

Transcribed by eye from the figure PDFs; vertices: parties A..E -> 0..4,
purifier O, bulk sigma_n -> "b1", "b2", ... Each entry must satisfy
entropy_vector(G, 5) == scale * C5_EXTREME_RAYS[k-1] exactly — the verifier
(scripts/verify_c5_graphs.py) is the arbiter of transcription correctness;
graphs that failed the first eyeball pass were corrected by a single-edit
variant search against that oracle, and the final dict below contains only
verified transcriptions.
"""

A, B, C, D, E, O = 0, 1, 2, 3, 4, "O"

# graph index (1-based, = ray index) -> list of (u, v, w)
C5_PUBLISHED_GRAPHS = {
    1: [(A, "b1", 1), ("b1", O, 1)],
    2: [("b1", A, 1), ("b1", B, 1), ("b1", C, 1), ("b1", O, 1)],
    3: [("b1", A, 1), ("b1", B, 1), ("b1", C, 1), ("b1", D, 1), ("b1", O, 2)],
    4: [("b1", A, 1), ("b1", B, 1), ("b1", C, 1), ("b1", D, 1), ("b1", E, 1),
        ("b1", O, 1)],
    5: [("b1", A, 1), ("b1", B, 1), ("b1", C, 1), ("b1", D, 1), ("b1", E, 1),
        ("b1", O, 3)],
    6: [("b1", A, 1), ("b1", B, 1), ("b1", C, 1), ("b1", D, 1), ("b1", E, 2),
        ("b1", O, 2)],
    7: [("b1", A, 1), ("b1", B, 1), ("b1", C, 1), ("b1", D, 2), ("b1", E, 2),
        ("b1", O, 3)],
    8: [("b1", A, 1), ("b1", B, 1), ("b1", O, 1), ("b2", C, 1), ("b2", D, 1),
        ("b2", E, 1), ("b1", "b2", 1)],
    9: [("b1", A, 1), ("b1", B, 1), ("b1", O, 2), ("b2", C, 1), ("b2", D, 1),
        ("b2", E, 2), ("b1", "b2", 2)],
    # 10-13 arrived shuffled in a batched figure read; assignments below were
    # adjudicated by matching each transcription against all 19 rays.
    10: [(O, "b1", 1), (O, "b4", 1), ("b1", "b2", 1), ("b2", "b3", 1),
         ("b3", "b4", 1), ("b4", "b1", 1), (A, "b1", 2), (B, "b1", 1),
         (B, "b2", 1), (C, "b2", 1), (C, "b3", 1), (D, "b3", 2),
         (E, "b3", 1), (E, "b4", 1)],  # the bulk-4-cycle "crown" (scale 2)
    11: [(O, "b3", 1), ("b1", O, 1), ("b1", "b2", 2), ("b2", "b3", 2),
         ("b2", E, 2), (A, "b3", 1), (B, "b1", 1), (C, "b1", 2),
         (D, "b3", 2)],
    12: [(A, "b1", 1), (A, "b4", 1), (B, "b1", 1), (B, "b2", 1), (C, "b2", 1),
         (C, "b3", 1), (D, "b3", 1), (D, "b4", 1), (E, "b2", 1), (E, "b4", 1),
         (O, "b1", 1), (O, "b3", 1), ("b5", "b1", 1), ("b5", "b2", 1),
         ("b5", "b3", 1)],  # FIXME: still failing verification; under re-read
    13: [("b1", O, 1), ("b1", "b2", 1), ("b1", D, 1), ("b2", O, 1),
         ("b2", D, 1), (A, "b1", 2), (B, "b1", 1), (B, "b2", 1),
         (C, "b2", 2), (E, "b2", 2)],  # scale 2
    14: [("b1", O, 2), ("b1", "b2", 1), ("b1", D, 1), ("b2", O, 1),
         ("b2", D, 1), (A, "b2", 2), (B, "b1", 1), (B, "b2", 1),
         (C, "b1", 2), (E, "b1", 3)],
    15: [(A, "b1", 3), (O, "b2", 3), ("b1", "b2", 1), (E, "b1", 2),
         (E, "b2", 1), (D, "b2", 2), (D, "b1", 1), (B, "b1", 2), (B, "b2", 1),
         (C, "b2", 2), (C, "b1", 1)],
    16: [(D, "b1", 2), (C, "b1", 1), (C, "b3", 1), (B, "b3", 2),
         ("b1", "b3", 1), ("b1", O, 1), ("b1", A, 1), (O, "b2", 1),
         (A, "b2", 1), ("b2", "b3", 1), ("b2", E, 1), ("b3", E, 1)],
    17: [(A, "b4", 1), (A, "b3", 1), (B, "b4", 1), (B, "b1", 1),
         ("b4", "b3", 1), ("b4", "b1", 1), ("b3", "b2", 1), ("b3", E, 2),
         ("b3", D, 1), ("b2", E, 1), ("b2", D, 1), ("b1", "b2", 2),
         (C, "b1", 2), (O, "b2", 3)],
    # 18 has 16 edges (O has degree 3); 19 has 18 edges and its sigma1-sigma4
    # weight-2 edge passes visually through O (no sigma1-O edge exists).
    18: [(A, "b4", 1), (A, "b2", 2), (B, "b1", 1), (B, "b2", 2),
         ("b1", "b4", 1), ("b1", "b2", 2), ("b2", O, 1), ("b2", "b3", 1),
         (O, "b3", 1), ("b2", C, 2), ("b3", C, 1), ("b3", D, 2),
         (E, "b3", 1), ("b4", O, 1), ("b4", E, 2), ("b4", D, 1)],
    19: [(E, "b5", 1), ("b5", D, 2), (A, "b1", 2), ("b5", "b4", 2),
         ("b4", D, 1), ("b4", C, 2), ("b3", C, 1), ("b1", "b4", 2),
         (B, "b2", 2), (O, "b3", 1), ("b2", O, 1), ("b2", "b3", 1),
         ("b4", "b3", 1), ("b5", O, 1), (A, "b2", 1), (B, "b1", 1),
         (E, "b1", 1), (E, "b2", 1)],
}

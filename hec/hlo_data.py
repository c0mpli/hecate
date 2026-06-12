"""The He-Lee-Ooguri graph realizations of mystery orbits {146, 180, 181}.

Edge lists transcribed from the explicit display in arXiv:2601.19979 (tex
source, after eq. block at 'we also for clarity represent each graph as a
collection of weighted edges'); repository
github.com/Jaeha0526/EntropyCone_RL pinned at commit
193d994c8b3a2924a49ffb0f69ce7b0042f97108.

Independently verified here (scripts/verify_hlo.py): exact scaling 12x, 12x,
9x respectively; every graph is simple (one boundary vertex per party) and
CYCLIC — consistent with the chordality theorem, under which none of these
orbits admits a simple forest.

Vertex convention: parties A-F -> 0-5, purifier O, internal vertices "b1"...
"""

A, B, C, D, E, F, O = 0, 1, 2, 3, 4, 5, "O"


def _v(x):
    return x if isinstance(x, int) or x == "O" else None


HLO_GRAPHS = {
    146: {
        "scale": 12,
        "edges": [
            (A, "b2", 12), (A, "b11", 12), (B, "b5", 12), (B, "b6", 12),
            (C, "b1", 12), (C, "b3", 12), (D, "b2", 12), (D, "b5", 12),
            (D, "b9", 12), (E, "b2", 12), (E, "b6", 12), (E, "b7", 12),
            (F, "b6", 12), (F, "b10", 12), (F, "b11", 12), (O, "b1", 12),
            (O, "b5", 12), (O, "b11", 12), ("b1", "b3", 8), ("b1", "b4", 6),
            ("b1", "b6", 12), ("b1", "b7", 6), ("b1", "b8", 7),
            ("b2", "b10", 12), ("b3", "b4", 6), ("b3", "b7", 4),
            ("b3", "b8", 8), ("b3", "b10", 12), ("b4", "b7", 2),
            ("b4", "b8", 3), ("b4", "b10", 6), ("b5", "b8", 12),
            ("b7", "b8", 6), ("b7", "b10", 6), ("b9", "b10", 12),
            ("b10", "b11", 12),
        ],
    },
    180: {
        "scale": 12,
        "edges": [
            (A, "b5", 12), (A, "b7", 12), (B, "b1", 12), (B, "b3", 12),
            (C, "b4", 12), (C, "b6", 12), (D, "b1", 12), (D, "b5", 12),
            (D, "b6", 12), (E, "b3", 12), (E, "b6", 12), (E, "b7", 12),
            (F, "b3", 12), (F, "b4", 12), (F, "b5", 12), (O, "b1", 12),
            (O, "b2", 12), (O, "b7", 12), ("b1", "b2", 7), ("b1", "b4", 12),
            ("b2", "b4", 12), ("b3", "b4", 12), ("b4", "b6", 12),
            ("b5", "b6", 12), ("b6", "b7", 12),
        ],
    },
    181: {
        "scale": 9,
        "edges": [
            (A, "b1", 9), (A, "b6", 9), (B, "b2", 9), (B, "b10", 9),
            (C, "b4", 9), (C, "b7", 9), (D, "b6", 9), (D, "b8", 4),
            (D, "b9", 5), (D, "b10", 9), (E, "b1", 9), (E, "b2", 9),
            (E, "b8", 9), (F, "b2", 9), (F, "b6", 9), (F, "b7", 9),
            (O, "b1", 9), (O, "b7", 9), (O, "b10", 9), ("b1", "b5", 9),
            ("b2", "b4", 9), ("b3", "b5", 6), ("b3", "b8", 6),
            ("b4", "b5", 9), ("b4", "b10", 9), ("b5", "b6", 9),
            ("b5", "b7", 9), ("b5", "b8", 9), ("b5", "b9", 5),
        ],
    },
}

HLO_COMMIT = "193d994c8b3a2924a49ffb0f69ce7b0042f97108"

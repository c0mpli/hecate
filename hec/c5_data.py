"""The 5-party holographic entropy cone, transcribed from arXiv:1903.09148.

Tables 1 and 2 of Hernandez Cuenca, "The holographic entropy cone for five
regions" (Phys. Rev. D 100, 026004; arXiv:1903.09148). Inequalities are kept
symbolic (subset-label -> coefficient) and converted to 31-vectors in code;
ray vectors use the paper's ordering (size, then lex — see hec.subsets).

Transcription is validated, not trusted: tests check that the Sym(6) orbit
sizes match the paper's quoted lengths (15, 20, 45, 72, 10, 60, 60, 90 -> 372
facets; ray orbits -> 2267 rays), that every ray satisfies all 372 facet
instances, and that every ray is extreme (saturated-facet rank 30).
"""

# (name, LHS terms, RHS terms) meaning  sum LHS >= sum RHS.
C5_INEQUALITIES = [
    ("SA", {"A": 1, "B": 1}, {"AB": 1}),
    ("MMI1", {"AB": 1, "AC": 1, "BC": 1}, {"A": 1, "B": 1, "C": 1, "ABC": 1}),
    (
        "MMI2",
        {"ABC": 1, "ADE": 1, "BCDE": 1},
        {"A": 1, "BC": 1, "DE": 1, "ABCDE": 1},
    ),
    (
        "QCyclic",
        {"ABC": 1, "ABD": 1, "ACE": 1, "BDE": 1, "CDE": 1},
        {"AB": 1, "AC": 1, "BD": 1, "CE": 1, "DE": 1, "ABCDE": 1},
    ),
    (
        "Q2",
        {
            "ABC": 1, "ABD": 1, "ABE": 1, "ACD": 1, "ACE": 1,
            "ADE": 1, "BCE": 1, "BDE": 1, "CDE": 1,
        },
        {
            "AB": 1, "AC": 1, "AD": 1, "BE": 1, "CE": 1, "DE": 1,
            "BCD": 1, "ABCE": 1, "ABDE": 1, "ACDE": 1,
        },
    ),
    (
        "Q3",
        {
            "ABC": 3, "ABD": 3, "ABE": 1, "ACD": 1, "ACE": 3,
            "ADE": 1, "BCD": 1, "BCE": 1, "BDE": 1, "CDE": 1,
        },
        {
            "AB": 2, "AC": 2, "AD": 1, "AE": 1, "BC": 1, "BD": 2,
            "CE": 2, "DE": 1, "ABCD": 2, "ABCE": 2, "ABDE": 1, "ACDE": 1,
        },
    ),
    (
        "Q4",
        {"ABC": 2, "ABD": 1, "ABE": 1, "ACD": 1, "ADE": 1, "BCE": 1, "BDE": 1},
        {
            "AB": 1, "AC": 1, "AD": 1, "BC": 1, "BE": 1, "DE": 1,
            "ABCD": 1, "ABCE": 1, "ABDE": 1,
        },
    ),
    (
        "Q5",
        {"AD": 1, "BC": 1, "ABE": 1, "ACE": 1, "ADE": 1, "BDE": 1, "CDE": 1},
        {
            "A": 1, "B": 1, "C": 1, "D": 1, "AE": 1, "DE": 1,
            "BCE": 1, "ABDE": 1, "ACDE": 1,
        },
    ),
]

EXPECTED_FACET_ORBIT_SIZES = [15, 20, 45, 72, 10, 60, 60, 90]  # sum = 372
TOTAL_FACETS = 372

# Table 2: one representative per extreme-ray orbit, paper ordering
# (A,B,C,D,E; AB,AC,AD,AE,BC,BD,BE,CD,CE,DE; ABC,ABD,ABE,ACD,ACE,ADE,BCD,
#  BCE,BDE,CDE; ABCD,ABCE,ABDE,ACDE,BCDE; ABCDE).
C5_EXTREME_RAYS = [
    (1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1),
    (1, 1, 1, 0, 0, 2, 2, 1, 1, 2, 1, 1, 1, 1, 0, 1, 2, 2, 2, 2, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1),
    (1, 1, 1, 1, 0, 2, 2, 2, 1, 2, 2, 1, 2, 1, 1, 3, 3, 2, 3, 2, 2, 3, 2, 2, 2, 2, 3, 3, 3, 3, 2),
    (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1),
    (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 3),
    (1, 1, 1, 1, 2, 2, 2, 2, 3, 2, 2, 3, 2, 3, 3, 3, 3, 4, 3, 4, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 2),
    (1, 1, 1, 2, 2, 2, 2, 3, 3, 2, 3, 3, 3, 3, 4, 3, 4, 4, 4, 4, 5, 4, 4, 5, 5, 5, 5, 4, 4, 4, 3),
    (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 2, 2, 2, 2, 2, 1),
    (1, 1, 1, 1, 2, 2, 2, 2, 3, 2, 2, 3, 2, 3, 3, 3, 3, 4, 3, 4, 4, 3, 4, 4, 2, 4, 3, 3, 3, 3, 2),
    (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 2, 3, 3, 2, 2, 2, 2, 2, 2, 1),
    (1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 3, 5, 3, 5, 4, 4, 4, 4, 3, 3, 2),
    (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 3, 3, 2, 3, 2, 3, 2, 2, 2, 2, 2, 2, 1),
    (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 3, 3, 3, 3, 3, 2, 3, 2, 2, 2, 2, 2, 2, 1),
    (2, 2, 2, 2, 3, 4, 4, 4, 5, 4, 4, 5, 4, 5, 5, 6, 4, 7, 6, 7, 7, 6, 5, 7, 5, 6, 5, 5, 5, 5, 3),
    (3, 3, 3, 3, 3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 5, 9, 7, 7, 9, 9, 9, 9, 6, 6, 6, 6, 6, 3),
    (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 2, 3, 3, 2, 2, 3, 3, 2, 2, 2, 2, 2, 1),
    (2, 2, 2, 2, 3, 4, 4, 4, 5, 4, 4, 5, 4, 5, 5, 4, 6, 5, 6, 7, 5, 6, 7, 7, 7, 6, 5, 5, 5, 5, 3),
    (3, 3, 3, 3, 3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 9, 7, 9, 9, 7, 7, 9, 9, 7, 6, 6, 6, 6, 6, 3),
    (3, 3, 3, 3, 3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 9, 5, 7, 9, 7, 9, 9, 9, 7, 6, 6, 6, 6, 6, 3),
]

TOTAL_EXTREME_RAYS = 2267

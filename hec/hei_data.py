"""Loader for the Czech et al. inequality data (arXiv:2309.06296 ancillary).

HEIvectors.txt: 1877 known 6-party holographic entropy inequalities (the
last line has no trailing newline, so `wc -l` reports 1876), one per line,
as 63 tab-separated integer coefficients in (size, lex) subset order,
convention  coeffs . S >= 0.

The ordering/sign convention is cross-checked at load time against
independently constructed SA and MMI lines (the file's first two entries),
and validated at scale by check-on-random-graphs (scripts/verify_hei6.py).
"""

from __future__ import annotations

import pathlib

from hec.cone import ineq_to_coeffs
from hec.subsets import vector_to_paper

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "2309.06296" / "anc"


def load_hei6(path: pathlib.Path | None = None) -> list[tuple[int, ...]]:
    """All 1877 known 6-party HEIs as 63-coeff paper-order tuples."""
    path = path or DATA / "HEIvectors.txt"
    ineqs = []
    for line in path.read_text().strip().splitlines():
        row = tuple(int(x) for x in line.split())
        if len(row) != 63:
            raise ValueError(f"expected 63 coefficients, got {len(row)}")
        ineqs.append(row)
    if len(ineqs) != 1877:
        raise ValueError(f"expected 1877 inequalities, got {len(ineqs)}")

    # convention check: line 1 must be SA(A,B), line 2 must be MMI(A,B,C)
    sa = vector_to_paper(ineq_to_coeffs({"A": 1, "B": 1}, {"AB": 1}, 6), 6)
    mmi = vector_to_paper(
        ineq_to_coeffs(
            {"AB": 1, "AC": 1, "BC": 1}, {"A": 1, "B": 1, "C": 1, "ABC": 1}, 6
        ),
        6,
    )
    if ineqs[0] != sa or ineqs[1] != mmi:
        raise ValueError("HEIvectors.txt ordering/sign convention mismatch")
    return ineqs

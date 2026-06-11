"""Subset bookkeeping: bitmasks, labels, and the (size, lex) paper ordering.

The literature orders the 2**n - 1 polychromatic indices by cardinality and
lexicographically within each cardinality: A, B, ..., AB, AC, ..., ABC...
(arXiv:1903.09148 Table 2 footnote; the Czech et al. ancillary files use the
same convention at n=6). paper_order(n) maps positions in that ordering to
our bitmasks.
"""

from __future__ import annotations

from functools import lru_cache

from hec.entropy import subset_label


@lru_cache(maxsize=None)
def paper_order(n: int) -> tuple[int, ...]:
    """Masks of all nonempty party subsets, sorted by (size, label)."""
    return tuple(
        sorted(range(1, 1 << n), key=lambda m: (bin(m).count("1"), subset_label(m, n)))
    )


def mask_of_label(label: str) -> int:
    m = 0
    for ch in label:
        m |= 1 << (ord(ch) - ord("A"))
    return m


def vector_from_paper(entries, n: int) -> dict[int, int]:
    """Entries listed in paper order -> {mask: value}."""
    order = paper_order(n)
    if len(entries) != len(order):
        raise ValueError(f"expected {len(order)} entries, got {len(entries)}")
    return {m: v for m, v in zip(order, entries)}


def vector_to_paper(v: dict[int, int], n: int) -> tuple:
    return tuple(v[m] for m in paper_order(n))

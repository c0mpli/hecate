"""Universal holographic entropy inequalities, checked on entropy vectors.

These are the inequality families every holographic entropy vector must
satisfy (and, for n <= 3 parties, they cut out the whole cone —
arXiv:1505.07839):

  SA   subadditivity            S(X) + S(Y)  >= S(XY)
  AL   Araki-Lieb               S(XY)        >= |S(X) - S(Y)|
  SSA  strong subadditivity     S(XY) + S(YZ) >= S(Y) + S(XYZ)
  WM   weak monotonicity        S(XY) + S(YZ) >= S(X) + S(Z)
  MMI  monogamy of mutual info  S(XY) + S(XZ) + S(YZ) >= S(X) + S(Y) + S(Z) + S(XYZ)

X, Y, Z range over disjoint nonempty subsets of the parties. AL and WM are
the purifications of SA and SSA, so on graph-model vectors (where the
purifier is just another boundary vertex) they are not independent checks —
but they exercise different subsets, which is exactly what an engine test
wants. MMI is holographic-only: generic quantum states may violate it
(the 4-qubit GHZ state does), graph min-cut vectors never do.

Instances involving the purifier inside X/Y/Z are equivalent by purification
to instances over party subsets only, so checking all disjoint party subsets
covers the full Sym(n+1)-orbit of each family.
"""

from __future__ import annotations

from hec.entropy import subset_label


def check_vector(S: dict[int, object], n: int) -> list[tuple]:
    """Return every violated inequality instance as (name, subsets..., slack).

    Empty list means the vector satisfies SA, AL, SSA, WM and MMI. slack is
    LHS - RHS (negative iff violated; exact if the entropies are exact).
    """
    full = (1 << n) - 1
    masks = range(1, full + 1)
    bad: list[tuple] = []

    for X in masks:
        for Y in masks:
            if X & Y:
                continue
            if Y > X:  # SA and AL are symmetric in X, Y
                sa = S[X] + S[Y] - S[X | Y]
                if sa < 0:
                    bad.append(("SA", X, Y, sa))
                al = S[X | Y] - abs(S[X] - S[Y])
                if al < 0:
                    bad.append(("AL", X, Y, al))
            for Z in masks:
                if Z & (X | Y) or Z <= X:  # SSA and WM are symmetric in X, Z
                    continue
                ssa = S[X | Y] + S[Y | Z] - S[Y] - S[X | Y | Z]
                if ssa < 0:
                    bad.append(("SSA", X, Y, Z, ssa))
                wm = S[X | Y] + S[Y | Z] - S[X] - S[Z]
                if wm < 0:
                    bad.append(("WM", X, Y, Z, wm))
                if Z > Y > X:  # MMI is symmetric in X, Y, Z
                    mmi = (
                        S[X | Y] + S[X | Z] + S[Y | Z]
                        - S[X] - S[Y] - S[Z] - S[X | Y | Z]
                    )
                    if mmi < 0:
                        bad.append(("MMI", X, Y, Z, mmi))
    return bad


def describe_violation(v: tuple, n: int) -> str:
    name, *rest = v
    slack = rest[-1]
    subsets = ", ".join(subset_label(m, n) for m in rest[:-1])
    return f"{name}({subsets}) violated by {-slack}"

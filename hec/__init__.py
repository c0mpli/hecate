"""hec — holographic entropy cone toolkit.

Day-1 scope (SPEC.md): graph-model entropy engine + universal inequality
checks. cone.py / prover.py / realize.py / falsify.py / search.py / db.py
arrive with M1-M3.
"""

from hec.entropy import PURIFIER, entropy_vector, subset_label
from hec.inequalities import check_vector

__all__ = ["PURIFIER", "entropy_vector", "subset_label", "check_vector"]

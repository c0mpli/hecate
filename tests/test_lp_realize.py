"""LP cut-assignment realizer: finds and exactly certifies known rays."""

import random

from hec.c5_data import C5_EXTREME_RAYS
from hec.entropy import entropy_vector
from hec.lp_realize import lp_realize_target
from hec.subsets import vector_from_paper


def test_lp_realizes_known_rays():
    for idx in (1, 4):  # Bell pair; 6-party perfect tensor
        ray = C5_EXTREME_RAYS[idx - 1]
        hit = lp_realize_target(ray, 5, random.Random(11), attempts=25)
        assert hit is not None, f"ray {idx} not realized"
        G, k = hit
        want = {m: k * v for m, v in vector_from_paper(ray, 5).items()}
        assert entropy_vector(G, 5) == want

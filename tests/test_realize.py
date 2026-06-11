"""Realizer scaffold: known-realizable rays get found and verified exactly."""

import random

from hec.c5_data import C5_EXTREME_RAYS
from hec.entropy import entropy_vector
from hec.realize import realize_target
from hec.subsets import vector_from_paper


def test_realizes_bell_pair_and_star_ray():
    for idx in (1, 2):  # ray 1 = Bell pair A-O; ray 2 = 4-party perfect tensor
        ray = C5_EXTREME_RAYS[idx - 1]
        rng = random.Random(42)
        hit = realize_target(ray, 5, rng, restarts=60, moves=1200)
        assert hit is not None, f"ray {idx} not realized"
        G, k = hit
        tgt = {m: k * v for m, v in vector_from_paper(ray, 5).items()}
        assert entropy_vector(G, 5) == tgt

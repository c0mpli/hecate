"""Cross-backend agreement: igraph fast path == networkx reference, exactly."""

import random

from hec.entropy import entropy_vector, entropy_vector_fast
from hec.graphs import random_mixture


def test_igraph_matches_networkx():
    rng = random.Random(99)
    for n in (3, 4, 5):
        for _ in range(120):
            G = random_mixture(n, rng)
            assert entropy_vector_fast(G, n) == entropy_vector(G, n)

"""seed_search: stabilizer images realize the same ray and reduce (validation
on a known-reducible C5 ray; no slow LP in CI)."""

import pathlib
from fractions import Fraction

import networkx as nx

from hec.c5_data import C5_EXTREME_RAYS
from hec.c5_graphs import C5_PUBLISHED_GRAPHS
from hec.cycle_surgery import surgery
from hec.entropy import entropy_vector, entropy_vector_labeled
from hec.seed_search import _graph, relabel_edges, stabilizer, structure_key
from hec.subsets import vector_from_paper


def test_stabilizer_image_realizes_same_ray():
    ray = C5_EXTREME_RAYS[9]  # ray 10
    base = [(u, v, w) for u, v, w in C5_PUBLISHED_GRAPHS[10]]
    G0, p0 = _graph(base, 5)
    v0 = entropy_vector_labeled(G0, 5, p0)
    stab = [s for s in stabilizer(ray, 5) if s != tuple(range(6))]
    assert stab, "ray 10 should have a nontrivial stabilizer"
    img = relabel_edges(base, stab[0], 5)
    G1, p1 = _graph(img, 5)
    assert entropy_vector_labeled(G1, 5, p1) == v0  # same ray, exact


def test_surgery_reduces_a_stabilizer_image(tmp_path):
    ray = C5_EXTREME_RAYS[9]
    base = [(u, v, w) for u, v, w in C5_PUBLISHED_GRAPHS[10]]
    stab = [s for s in stabilizer(ray, 5) if s != tuple(range(6))]
    img = relabel_edges(base, stab[0], 5)
    G, party = _graph(img, 5)
    tgt = entropy_vector_labeled(G, 5, party)
    path, info = surgery(G, party, 5, "c5_10", target=tgt, max_nodes=6000,
                         out_dir=tmp_path, log=lambda m: None)
    assert info["status"] == "tree"


def test_structure_key_collapses_symmetry_copies():
    base = [(u, v, w) for u, v, w in C5_PUBLISHED_GRAPHS[10]]
    ray = C5_EXTREME_RAYS[9]
    stab = [s for s in stabilizer(ray, 5) if s != tuple(range(6))]
    G0, p0 = _graph(base, 5)
    G1, p1 = _graph(relabel_edges(base, stab[0], 5), 5)
    # symmetry image: identical party-blind structure
    assert structure_key(G0, p0) == structure_key(G1, p1)

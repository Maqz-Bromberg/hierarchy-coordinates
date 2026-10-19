"""Hierarchy coordinates (Corominas-Murtra et al. 2013) on graphs with known values."""

import networkx as nx
import numpy as np
import pytest

from hierarchy_coordinates import graph_entropy, hierarchy_coordinates
from hierarchy_coordinates.coordinates import thresholds_for


def balanced_tree(branching, height):
    return nx.to_numpy_array(nx.balanced_tree(branching, height, create_using=nx.DiGraph))


def test_trees_with_equal_leaf_depth_are_perfectly_hierarchical():
    """Lemma in appendix D: T = F = O = 1 for directed trees whose leaves all have the same length."""
    for b, h in [(2, 1), (2, 3), (3, 2)]:
        hc = hierarchy_coordinates(balanced_tree(b, h))
        assert hc == pytest.approx((1.0, 1.0, 1.0))


def test_star_is_perfectly_hierarchical():
    A = np.zeros((7, 7))
    A[0, 1:] = 1
    assert hierarchy_coordinates(A) == pytest.approx((1.0, 1.0, 1.0))


def test_inverted_tree_has_negative_treeness():
    hc = hierarchy_coordinates(balanced_tree(2, 3).T)
    assert hc.treeness == pytest.approx(-1.0)


def test_directed_cycle_is_not_orderable():
    n = 6
    A = np.roll(np.eye(n), 1, axis=1)
    assert hierarchy_coordinates(A).orderability == 0.0


def test_fork_entropies():
    """a -> {b, c}: following the flow has one binary choice (H_f = ln 2); reversing it has none (H_b = 0)."""
    G = nx.DiGraph([(0, 1), (0, 2)])
    assert graph_entropy(G, forward=True) == pytest.approx(np.log(2))
    assert graph_entropy(G, forward=False) == 0.0


def test_matrix_powers_weight_entropy_by_reach():
    """Diamond with a tail: 0 -> {1, 2} -> 3 -> 4. Reversing from 4 crosses node 3 (two parents) with
    probability 1, so H_b = ln 2; following the flow, the only choice is at 0, so H_f = ln 2."""
    G = nx.DiGraph([(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)])
    assert graph_entropy(G, forward=False) == pytest.approx(np.log(2))
    assert graph_entropy(G, forward=True) == pytest.approx(np.log(2))


def test_backward_entropy_is_weighted_by_reach():
    """0 -> 1 <- 2 and 3 -> 4. Reversing from the two minimal nodes {1, 4}: only the walk from 1 meets a choice
    (k_in(1) = 2), so H_b = (ln 2) / 2, not the ln 2 of summing log k_in over every non-maximal node."""
    G = nx.DiGraph([(0, 1), (2, 1), (3, 4)])
    assert graph_entropy(G, forward=False) == pytest.approx(np.log(2) / 2)


def test_unreachable_choices_do_not_count():
    """0 -> 1 -> 2 and 3 -> 4 <- 5: the fork into 4 is met only by the walk from 4, so it is charged once of two."""
    G = nx.DiGraph([(0, 1), (1, 2), (3, 4), (5, 4)])
    assert graph_entropy(G, forward=False) == pytest.approx(np.log(2) / 2)


def test_exponential_thresholds_span_the_weights():
    """Exponential thresholds start above the smallest weight, not near 0, and end at the largest."""
    A = np.array([[0.5, 1.0], [0.7, 0.9]])
    th = thresholds_for(A, 8, exp_threshold_distribution=0.5)
    assert len(th) == 8
    assert min(th) > 0.5
    assert max(th) == pytest.approx(1.0)

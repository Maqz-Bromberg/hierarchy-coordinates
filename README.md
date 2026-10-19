# Hierarchy coordinates

Treeness T, feedforwardness F and orderability O of weighted directed graphs, following Corominas-Murtra, Goñi, Solé
& Rodríguez-Caso, [*On the origins of hierarchy in complex networks*](https://arxiv.org/abs/1303.2503), PNAS 110:13316
(2013). Together the three numbers place a network in a "hierarchy morphospace": a directed tree whose leaves all sit at
the same depth has (T, F, O) = (1, 1, 1), an inverted tree has T = −1, and a directed cycle has O = 0.

This package replaces [Hierarchy_Coordinates](https://github.com/MaxBromberg/Hierarchy_Coordinates) (2021); see
[Migrating from the 2021 package](#migrating-from-the-2021-package).

```sh
pip install -e .            # numpy and networkx only
pip install -e ".[dev]" && pytest
```

```python
import numpy as np
from hierarchy_coordinates import hierarchy_coordinates

A = np.random.default_rng(0).random((10, 10))   # A[i, j] is the weight of the edge i -> j
hc = hierarchy_coordinates(A)
hc.treeness, hc.feedforwardness, hc.orderability
```

## How it works

The paper defines the coordinates for unweighted graphs. A weighted graph is handled as in Bromberg (2020):

1. Threshold the weights into binary graphs (`num_thresholds=8`, spaced linearly from the smallest weight to the
   largest; `exp_threshold_distribution=0.5` spaces them exponentially as in the thesis). A binary matrix uses a
   single threshold. The exponential thresholds differ from the thesis code in two ways. The thesis scaled them by
   (max − min) without adding min, so they started near 0 rather than at the smallest weight; here they are offset by
   min. Its top threshold also equalled the largest weight, so that graph had no edges and added (T, F, O) = (0, 0, 1)
   to the average; here, as with the linear thresholds, every threshold is below the largest weight.
2. Condense each binary graph into a DAG of its strongly connected components, each node weighted by the number of
   original nodes it holds, and keep the largest weakly connected component.
3. Compute the coordinates of that DAG (appendix D of the paper):
   - **orderability O**: the fraction of nodes that are not part of a cycle;
   - **feedforwardness F**: how short paths from maximal (no incoming edges) to minimal (no outgoing edges) nodes are
     compared with the number of original nodes they pass through, averaged over the graph and its bottom-up pruned
     subgraphs (eq. D2);
   - **treeness T**: (H_f − H_b) / max(H_f, H_b), from the uncertainty of walking forward from the top (H_f) against
     walking backward from the bottom (H_b), averaged over the graph and its pruned subgraphs (eqs. D4–D9).
4. Average each coordinate over the thresholds.

`graph_entropy`, `treeness`, `feedforwardness`, `orderability` and `node_weighted_condense` are exported for use on
their own.

**One reading of the paper:** it prints the path-probability sums in eqs. D4 and D6 from k = 1. Taken literally, a
single fork a → {b, c} would have H_f = 0 and every directed tree T = 0, contradicting the paper's own Lemma (T = F = O
= 1 for trees with equal-depth leaves) and its Figs. 12–13. The k = 0 identity term is therefore included. The tests
check the Lemma cases.

## Migrating from the 2021 package

Treeness now follows the paper's definition (eqs. D4–D9), so its values differ from the 2021 package. With the
default linear thresholds, F and O are unchanged. Exponential thresholds are set by `exp_threshold_distribution` (the
2021 package's `threshold_distribution`) and use the thesis spacing with the two fixes in step 1, so all three
coordinates can differ when they are used.

The 2021 README documents `average_hierarchy_coordinates(A)` returning `(orderability, feedforwardness, treeness)`,
but its code defines `hierarchy_coordinates(A)` returning `(treeness, feedforwardness, orderability)`. This package
keeps the code's name and order, now as a named tuple.

## References

- B. Corominas-Murtra, J. Goñi, R. V. Solé, C. Rodríguez-Caso (2013). On the origins of hierarchy in complex networks.
  *PNAS* 110(33):13316–13321. [arXiv:1303.2503](https://arxiv.org/abs/1303.2503).
- M. Bromberg (2020). *Emergence of Hierarchy via Local Adaptation to Diffusion*. MSc thesis, Freie Universität
  Berlin. Code:
  [Networks_Via_Diffusion](https://github.com/MaxBromberg/Networks_Via_Diffusion).

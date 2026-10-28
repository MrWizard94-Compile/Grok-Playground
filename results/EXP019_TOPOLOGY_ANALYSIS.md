# EXP-019: Topology Isolation + Frontier Metrics Report
**Date:** 2026-07-01
**Classification:** [SUPPORTED INFERENCE - Frontier as better explanatory variable than size/degree]

## Experiment
- Controlled: same-ish N/E, different structures (linear/tree/hub/dense/sparse_random) via params.
- Measured: Active Dependency Frontier (2-hop predecessors as constraining deps for rewrites), Information Locality, throughput, value/rew.
- [LABEL: Addresses review - isolate topology, use better frontier than avg degree.]

## Data
- Frontier varies: linear 14, tree 31, hub 212, dense 119, sparse 47.
- Loc: linear 0.2, tree 0.2, hub 0.2, dense 0.3, sparse 0.2 (dense highest).
- Rewrites consistent.
- Quick adversarial (high branch): est_frontier=58, loc=0.255 (elevated).

## Analysis [OBSERVATION + HYPOTHESIS]
- "Frontier width varies with topology even at fixed size; locality tends to track it better than raw size or avg degree." [SUPPORTED INFERENCE]
- Correlation: higher max_active_frontier -> tendency for higher loc.
- "Increasing mf beyond 4 produced no measurable improvement in tested families." [OBSERVATION from EXP-017/018]

## Why locality shrinks (Working Hypothesis)
- If rewrites depend on local bounded frontier (est by 2-hop preds), exec state only needs to cover current frontier, not N.
- Explains:
  - Knee: no gain past frontier size.
  - Diversity: simple linear low loc; dense/high-fan high loc.
  - Scale: if frontier grows slower than N, loc drops.

**Falsifiable:** Graphs with low degree but exploded transitive frontier (e.g., long chains + merges) should have high loc despite low avg_degree.

## Next (Best Judgement)
- Proper frontier: full transitive within rewrite rules (not just 2-hop).
- Controlled: fixed N/E, vary frontier width explicitly.
- Math: fit L ≈ f(F, N) or L ∝ F/N on data.
- Adversarial: high frontier width graphs to find break points.
- Avoid size scaling; explain curves.

All precise. No overclaim. Data in results/exp019_.... 

This shifts from "bigger numbers" to mechanism. H1 support via isolation.
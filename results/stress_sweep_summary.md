# EP-GRM Stress Sweep — Aggregated Results

**Source:** results/epgrm_stress_sweep_20260701_015355.csv (96 runs)

## Peak Focus Scaling (Primary H1 Metric)

| Graph Nodes | Mean Peak Focus | Max Peak Focus | Runs |
|-------------|-----------------|----------------|------|
| 25          | 4.0             | 4              | 32   |
| 50          | 5.1             | 7              | 32   |
| 100         | 5.2             | 7              | 32   |

**Observation:** Increasing graph size 4x (25→100) increased mean peak focus by only ~1.2 nodes.

## Insensitivity to Stress Factors

| Factor      | Value | Mean Peak Focus |
|-------------|-------|-----------------|
| Branching   | 2     | 4.8             |
| Branching   | 5     | 4.7             |
| Cycles      | False | 4.8             |
| Cycles      | True  | 4.7             |
| Density     | 0.02  | 4.8             |
| Density     | 0.08  | 4.6             |

Peak focus showed almost no sensitivity to branching factor, cycles, or density.

## Other Metrics (averages)

- Avg total movement (proxy): 83
- Max observed peak focus across all runs: 7
- Configured max_focus in sweep: 10
- Success rate: 0% (rules too weak for acceptance threshold — focus bounded anyway)

## Live High-Stress Example (100 nodes, br=5, dense, cycles+edits)

- Peak focus: **5**
- Graph: 100 nodes, 895 edges
- Movement over 200 steps: 109
- Rewrites accepted: 200
- Peak mem (sim): ~1.1 MB

## Interpretation (narrow)

The current EP-GRM implementation kept active executive state (focus) between 4–7 on synthetic graphs up to 100 nodes with multiple stress factors applied. This is consistent with the bounded executive hypothesis on these workloads.

Full raw data available in the CSV.

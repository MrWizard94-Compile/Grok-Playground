# EXPERIMENT REGISTRY — Iteration 001

**Purpose:** Obsessive tracking of every experiment performed. Each entry has ID, date, classification, parameters, results summary, links to artifacts, and verdict on hypotheses.

## Experiment IDs

### EXP-001-LINEAR-BASE
**Date:** 2026-07-01  
**Type:** Baseline demonstration  
**Task:** Linear chain n=6, n=25  
**Classification:** [SUPPORTED]  
**Key Result:** peak_focus=3 for n=25  
**Artifacts:** experiments/run_linear_experiment.py, live runs  
**H1 Status:** Supported on linear tasks  
**Notes:** Focus remained constant while horizon = 25.

### EXP-002-STRESS-SWEEP-96
**Date:** 2026-07-01  
**Type:** Systematic falsification attempt  
**Parameters:** 
- node sizes: 25,50,100
- branching: 2,5
- density: 0.02,0.08
- cycles: on/off
- edits: 0,4
- max_focus=10
- 96 total runs (2 seeds each combo)
**Classification:** [IMPORTANT - FALSIFICATION ATTEMPT]
**Raw Data:** results/epgrm_stress_sweep_20260701_015355.csv
**Summary:** results/stress_sweep_summary.md
**Key Numbers:**
- Overall max peak_focus observed: 7
- Mean at 100 nodes: 5.2
- Almost no effect from cycles / branching / density
**Verdict on H1:** Not falsified. Growth is minimal.
**Verdict on Stress Robustness:** Passed this round of attacks.
**Limitation:** Rules made limited progress (0% "solved"). Measured boundedness under non-progressing conditions.

### EXP-003-LIVE-HIGH-STRESS-100
**Date:** 2026-07-01  
**Config:** 100 nodes, br=5, density=0.08, cycles=True, edits=4, max_focus=8, 200 steps
**Classification:** [LIVE REPRODUCIBLE]
**Results:**
- peak_focus = 5
- movement = 109
- rewrites_accepted = 200
- graph ended at 100 nodes / 895 edges
**Artifacts:** Direct execution output in session logs.
**Significance:** Confirms bounded focus even with 895 edges and noise.

### EXP-004-... (future)
Will be appended.

## Experiment Design Principles (Labeled)

- Every sweep must record full parameter matrix.
- Use at least two seeds for reproducibility check.
- Always log peak_focus, total_movement, verification work, graph final size.
- When progress is low, reframe success criterion to "bounded over long horizon" and record it explicitly.
- Publish raw CSVs + summary tables.

## How to Add New Experiment
1. Give it an ID (EXP-00X-DESCRIPTIVE).
2. Record in this file with classification.
3. Update CLAIMS_REGISTRY.md if it affects a claim.
4. Commit the CSV + plots + this registry update.

**Current focus of new experiments:** Make rules/scheduler strong enough to drive actual synthesis progress on stressed graphs, then re-measure the same boundedness + movement metrics.

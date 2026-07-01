# RESEARCH MANIFEST — EP-GRM (Explicit Persistent Graph Rewrite Machine)
**Iteration:** 001  
**Protocol:** Autonomous Research System v2.0  
**Date Generated:** 2026-07-01  
**Classification Level:** [DOCUMENT - ESTABLISHED]

## Purpose of This File
This is the obsessive central index. Every major artifact is listed, versioned, and labeled with its scientific status.

## Directory Map (Labeled)

### Core Source (Implementation)
- `src/core.py` [ESTABLISHED] — VersionedGraph, FocusSet (enforces bound), RewriteRule primitives.
- `src/metrics.py` [ESTABLISHED] — Rich instrumentation (node visits, rewrites, focus dynamics, etc.).
- `src/epgrm_sim.py` [ESTABLISHED + INSTRUMENTED] — Main simulator loop. All progress via verified local rewrites on persistent graph.
- `src/tasks/linear_chain.py` [SUPPORTED - T1] — Controllable linear synthesis benchmark.
- `src/tasks/stress.py` [WORKING - Stress Generator] — Adversarial graph generator for falsification attempts.
- `src/baselines.py` [SUPPORTED - Pessimistic] — Naive full-reload models for relative movement comparison only.

### Experiments & Runners
- `experiments/stress_sweep.py` [WORKING] — 96-run parameter sweep across stress dimensions.
- `experiments/run_linear_experiment.py` [SUPPORTED] — Basic linear demonstration.

### Results & Evidence (Labeled Data)
- `results/stress_sweep_summary.md` [SUPPORTED INFERENCE]
- `results/epgrm_stress_sweep_20260701_015355.csv` [RAW DATA - 96 runs]
- `results/iteration001_early_results.md` [CLASSIFIED CLAIMS]
- `plots/` [to be populated] — Generated visualizations with labels.

### Phase Documentation
All in `iterations/001/` — follow exact 10-phase workflow. Each phase document carries classification headers.

### Logs
- `logs/RESEARCH_LOG.md` — Living record. Every entry classified.

## Current Research State Labels (2026-07-01)

**Established Facts (about this specific implementation):**
- EP-GRM simulator exists and enforces bounded focus.
- Focus size remained 4-7 across 25-100 node graphs under multiple stress factors.
- All runs are deterministic for given seed + rules.
- Instrumentation captures node visits, rewrites, movement proxy, etc.

**Supported Inferences (narrow):**
- On linear-chain and synthetic stress graphs, active executive state scales very slowly with graph size.
- Data movement proxy is low relative to full-reload baselines.

**Working Hypotheses (still being tested):**
- H1: Bounded executive state is sufficient for synthesis tasks.
- H2: Local delta rewrites reduce data movement.
- Stress survival: The mechanisms will not explode focus when locality is attacked, cycles exist, etc.

**Open Falsification Efforts:**
- Increasing graph size, branching, density, cycles, random edits.
- Future: conflicting constraints, disconnected components, very deep dependency chains.

## Versioning & Labeling Convention Used
- [ESTABLISHED] — Properties of the current code + reproducible runs.
- [SUPPORTED INFERENCE] — Narrow conclusions from data vs specific baselines.
- [WORKING HYPOTHESIS] — Claims that require further falsification.
- [SPECULATION] — Ideas not yet testable.
- [NEGATIVE RESULT] — When a mechanism fails a test (valuable).
- [TODO / OPEN] — Planned next falsification.

## How to Read This Research
1. Start with `docs/CLAIMS_REGISTRY.md`
2. Read `results/stress_sweep_summary.md` for numbers.
3. Inspect raw CSVs.
4. Review code comments labeled with [CLASSIFICATION].
5. Never treat any claim as applying outside the exact experimental conditions described.

**This manifest is itself [DOCUMENT - ESTABLISHED] as of the timestamp above.**

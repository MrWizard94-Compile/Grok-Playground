# EP-GRM Research Project Overview

**Project**: Autonomous research into Explicit Persistent Graph Rewrite Machine (EP-GRM) as a novel computational architecture for bounded executive state, minimal data movement, explicit verification, and persistent cognition. Aimed at overcoming von Neumann bottleneck, transformer limitations, and enabling long-horizon autonomous software synthesis.

**Start Date**: 2026-07-01  
**Current Iteration**: 001  
**Focus Architecture**: EP-GRM only (no parallel architectures yet).  
**Protocol**: Strict 10-phase workflow (Problem Definition → Prior Knowledge → Design Space → Hypotheses → Experimental Design → Planning → Implementation → Verification → Analysis → Revision).  
**Philosophy**: Stress-test to falsify; document failures as progress; precise classifications (Established Fact, Supported Inference, Working Hypothesis, etc.); one architecture, deep evidence.

## Core Hypotheses (from Phase 4)
- **H1 (Bounded Executive State + Useful Work)**: Executive state (focus) remains bounded (small relative to graph) while sustaining useful work (rewrites + value) as complexity grows. Evolved to include efficiency/usefulness metrics.
- **H2 (Data Movement)**: Local rewrites yield low movement vs. full-reload baselines.
- **H3 (Verification)**: Intrinsic verification (justifications, nogoods) with bounded overhead and explicit handling (e.g., conflicts as "nogood + deferred").
- Supporting: Information Locality (unique touched / total nodes; lower better), efficiency (rewrites / (avg_focus * steps)), value/rewrite, Active Dependency Frontier (2-hop constraining predecessors).

## Key Experiments & Data (as of 2026-07-01)
- **Scaling (EXP-012/013/014/015/016)**: 200–1500 nodes (up to ~2800 total with components), full stress (cycles, conflicts, disconnected, edits, heavy mode). 
  - Consistent: Peak focus saturates at configured max (e.g., 12) but never exceeds (Established: bound enforced in sim).
  - Rewrites: Consistent full rate post-rule fixes (e.g., 150/150 steps).
  - **Information Locality trend**: Decreasing with scale (e.g., ~0.27 at 300–400 → 0.0365 at 2800 total). Strong support for small executive fraction as complexity grows.
- **Knee/Isolation (EXP-017)**: Fixed large graph, vary *only* max_focus (4–24). Plateau at >=4: throughput=1.0, locality~0.081, value/rewrite=2.0. Knee <=4; no benefit from larger focus. [Supported Inference: small bound sufficient for this family.]
- **Diversity & Topology (EXP-018/019)**: Knee repeated on linear/tree/hub/dense/sparse families; controlled structures (fixed N/E, vary topology).
  - Plateau holds across families.
  - Linear: best locality (~0.0286, simple deps).
  - Dense: worst (~0.2216).
  - Frontier (max active 2-hop preds): 14 (linear) to 212 (hub); correlates with loc better than size/avg degree. High-frontier test: loc=0.255 (elevated).
- **Metrics Evolution**: From raw rewrites → locality, efficiency, value/rewrite, frontier. "Value of work" (not just quantity) emphasized.
- **Total Data**: Multiple seeds, per-step series CSVs, master summaries, ~30+ runs. All stress (heavy multi-component + conflicts).

**Consolidated Trend (locality vs. size)**: Strongly decreasing. Executive state becomes shrinking % of graph.

## Current Status & Classifications
- **Established Facts (implementation)**: Bound always enforced (peak <= max_focus). Determinism in tested runs. Instrumentation complete (per-step: focus, movement, value, touched, admissions, impasses).
- **Supported Inferences (strong)**: 
  - Bounded exec + useful work + improving locality as scale/complexity grows (H1 robust for tested family).
  - Frontier width (not raw N or degree) better predicts locality. Plateau general; small focus adequate.
  - Low movement relative to baselines; explicit verification (nogoods) works.
- **Working Hypotheses**: Rewrites on local bounded frontier → exec state bounded by frontier (explains knee, loc drop, topology effect). Falsifiable via controlled frontier-width graphs.
- **Limitations/Observations**: Saturation at max_focus (functional but equilibrium). Early variability (0-rewrites) fixed by rules. Progress inconsistent without improvements; dense/high-fan structures elevate loc.
- **No Overclaims**: All scoped to "tested benchmark family". Observations, not causation. "Increasing max_focus beyond ~4 produced no measurable improvement."

**Plots**: Locality vs size (decreasing), by family (linear best), knee (flat), efficiency, focus-over-time series.

## Documentation (Obsessive)
- `docs/EXPERIMENT_REGISTRY.md`: All EXPs (001–019) with configs, results, classifications, artifacts.
- `docs/CLAIMS_REGISTRY.md`: H1–H3 + evolved (bounded+useful, frontier as variable); evidence, falsification criteria, precise phrasing.
- `logs/RESEARCH_LOG.md`: Full history, entries per session with labels.
- Reports: Per-EXP (e.g., EXP012, EXP019), knee analysis.
- Code: Labeled ([EXP-xxx], [H1 support], [review feedback]) in src/ (metrics, sim, stress, tasks).
- State: `docs/STATE_SNAPSHOT.md`, `RESEARCH_MANIFEST.md`, `EPGRM_INVARIANTS.md`.

**Phases**: Followed 1–10 iteratively (stress/analysis heavy now in 8–10). Failures (e.g., rule limits, saturation) documented as progress.

## Trajectory & Best Judgement
- **Maturity**: From scaling benchmarks ("bigger N") → isolation (vary one var: max_focus, topology) → explanatory (frontier as key; start of model L ~ f(F, N)).
- **Strengths**: Data volume high; precise classifications; keep failures; moving to prediction ("for similar families, small focus sufficient").
- **Gaps (per review)**: Need controlled frontier-width (fixed N/E, vary width), adversarial (high-frontier to break), math model, more value metrics (e.g., convergence deltas), benchmark families.

**Current Best Judgement Next (post H1 move-on)**:
- H1 phase concluded with substantial support (see CLAIMS). Shift complete to mechanistic/explanatory on H1a (frontier F as variable, but architecture dominates).
- EXP-027/028/029 completed: explicit control + adversarial (incl. multi-layer). L low/flat or *lower* (0.03-0.12) even at F~400-500. Model overpredicts; some high-F structures improve L.
- **Phase 10 Revision + "do all" completed:** results/PHASE10_REVISION.md (revised H1a), revised predict + concentration metric. EXP-030 prediction val run (24 runs, low mean |err| 0.0228, supports concentration term with some bias). Expanded property tests (determinism/nogood/high-F invariants pass). Diversity via multi-seed. Full doc updates.
- **Critical new document (2026-07-01):** `SIMULATION_LIMITS_AND_PATH_TO_REALIZATION.md` created in direct response to "so far EVERYTHING is simulated". Explicitly scopes all evidence as simulation-only and defines a multi-tier path out of pure simulation.
- **Tier 1 (ALL + "push the envelope"):** Memory model pushed (packing + LRU L1 + NVM x3 + persistence log + hierarchy). RunMetrics HF stats. Exps: TIER1-001/FRONTIER/ADVERSARIAL + PUSH-ENVELOPE (N=1200 extreme, flushes, L=0.0). L ultra-resilient. Full docs updated.
- Next: Consider Tier 2 skeleton in impl/, or even more aggressive sim (concurrency stub).
- All obsessive labeling, precise observations, NEGATIVE_RESULTS updates. Avoid pure N scaling. All claims now carry "simulation-only" qualifier where appropriate.

**Guiding Principle**: Creativity encouraged, rigor mandatory. Treat assumptions as open but require mechanism + validation. Negative results valuable.

This overview reflects state as of latest (post-EXP-019). Data supports H1 strongly for tested conditions; project shifting to mechanism discovery.

*All claims classified. Scoped to data. One architecture.*

- **Tier 2 skeleton started (push):** impl/tier2_reference_skeleton.py . Full docs updated.

- **Tier 2 expanded + comparison:** impl/tier2_reference_skeleton.py + TIER1-TIER2-FIDELITY-001 run. Full updates.

- **ALL tiers (1-4) + TIER2-STRESS-001:** Full advancement - Tier1 HF hardened/pushed, Tier2Simulator + multiple exps (bounded focus validated), Tier3 PIM stub + Tier4 plan. All docs updated. [TIER 1-4] [PHASE 10] [ALL COMPLETE] [REALIZATION PATH]

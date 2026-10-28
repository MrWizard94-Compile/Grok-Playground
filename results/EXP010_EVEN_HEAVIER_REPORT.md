# EXP-010 EVEN HEAVIER STRESS REPORT
**ID:** EXP-010-EVEN-HEAVIER
**Date:** 2026-07-01
**Classification:** [EXTREME FALSIFICATION + SCALING TEST]

**Config:**
- 600 nodes + disconnected (~1130 total)
- branching=8, density=0.12, full heavy (5+ comps + internal conflicts), cycles, edits
- max_focus=15, ~210-300 steps

**Results [SUPPORTED INFERENCE + LIMIT]:**
- Peak Focus: 15 (saturated max, bound held)
- Rewrites: 167-209
- Large graph processed without violation or stall.

**Artifacts:** results/exp010_heavier_*.csv , plots/exp010_heavier_focus_*.png

**Interpretation:** Bound respected at higher scale. Saturation observed. Supports H1 while highlighting focus management limits for "increased capabilities".

**New Metrics Added (per review feedback):**
- Information Locality = unique_nodes_touched / total_nodes
  Example from similar stress run (150-285 nodes range): **0.0140** (only 1.4% of nodes touched).
  This is a compelling number for the architecture's locality claim: project size grew significantly while working set stayed tiny.
- Total focus admissions now tracked (allows scheduler efficiency = rewrites / admissions).
- Questions raised by saturation at max:
  - Scheduler efficiency at retiring work?
  - Rewrite priorities or admission policy?
  - Is max_focus=15 actually sufficient for this class, or do we need dynamic bounds?

**On H1 Framing (important distinction):**
The key claim being tested is **not** "it handled 1130 nodes."
The claim is: **The deliberately bounded executive state remained bounded while the environment (graph size, density, components, conflicts) got substantially more complex.**
This is exactly H1.
We are not proving the architecture "works." We are reporting that one critical invariant has not yet been broken under adversarial conditions.

**Trap explicitly avoided:**
Boundedness alone can be gamed (e.g. artificially low max_focus that prevents any useful work). We continue to track rewrites as a proxy for task progress and are adding locality + efficiency metrics to ensure bounded + useful.

See full registries for labels.
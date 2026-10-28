# Phase 9: Objective Mechanistic Analysis — EP-GRM Frontier & Locality

**Date:** 2026-07-01
**Status:** Initial synthesis post H1 move-on (EXP-017 through EXP-028 + series)
**Classification:** [PHASE 9 ANALYSIS - SUPPORTED INFERENCES + OBSERVATIONS]

**Scope:** All data from knee/isolation (EXP-017/018), topology/frontier (EXP-019/020), controlled F (EXP-022/023/025/026/027), adversarial (EXP-028), heavy stress series (EXP-012+), and 56+ per-step series CSVs.

## Consolidated Patterns (Classified)

1. **Bound + Useful Work (H1 baseline) [ESTABLISHED + STRONG SUPPORTED INFERENCE]**
   - Bound always respected across 100+ runs up to 2000+ nodes + heavy stress.
   - In progressing runs (post rule fixes): rewrites ≈ steps (throughput 0.98-1.0).
   - Saturation at max_focus is normal operating mode for complex workloads (95%+ of steps in heavy runs); work continues efficiently.
   - Low per-step touch (~1 node) and low cumulative information locality.

2. **Knee / Sufficiency of Small Focus [OBSERVATION + SUPPORTED INFERENCE]**
   - EXP-017 (fixed large graph, mf=4..24): Plateau at mf>=4. No improvement in throughput (1.0), locality (~0.081), value/rewrite (2.0).
   - EXP-018 (diversity): Plateau holds on linear/tree/hub/dense/sparse. "Increasing max_focus beyond ~4 produced no measurable improvement in the recorded metrics."
   - Linear family: best L (~0.0286); dense: worst (~0.22) — topology matters.

3. **Frontier as Candidate Variable (H1a) [SUPPORTED INFERENCE with limits]**
   - EXP-019/020: At fixed N/E, frontier (2-hop active) varies 14-212+ across topologies. Locality tends to track F better than raw N or avg degree.
   - Controlled (EXP-025/026/027): Fixed N (900-1300), vary F via params or explicit generator.
     - obs_L consistently low: ~0.077 (025/026), 0.062-0.121 (027, mean ~0.103).
     - L flat or weakly responsive despite F variation (59-504 in 027).
   - EXP-028 adversarial (wide fan-in): Achieved F 64-108; mean L 0.1123 vs controlled ref 0.1091 (delta +0.0033). Extremely tight clustering.
   - Broader series: L decreases with scale while F grows slower in many families.

4. **Model Performance L ≈ c * (F / N) [LIMITED / WORKING HYPOTHESIS]**
   - Directional in uncontrolled/diverse data (higher F structures show tendency for higher L).
   - Poor in controlled/adversarial: overpredicts at high F (c=1.5); fitted c varies (0.17 prior controlled → 0.74 in EXP-027 batch; near-zero sensitivity in EXP-028).
   - EXP-029 (strong adv multi-layer): high F 397-459 yielded *lower* L (0.0295 mean) than high-F refs (0.0957). 
   - Best current description: L is low and largely *decoupled* from measured graph F within tested ranges. Architecture (local matching + bounded FocusSet + value-driven rules) imposes a strong cap. Some high-F topologies can even yield better L.
   - Refined candidate: L ≈ c * (effective_F / N) where effective_F << graph F due to focus policy and rewrite locality. F sets loose ceiling; execution model determines realized value.
   - Variance low post-saturation (stdev focus ~1.35 from series analysis).

5. **Negative / Boundary Results (valuable)**
   - Simple model incomplete (multiple controlled experiments).
   - Adversarial (current generators) insufficient to force elevated L.
   - Early rule robustness limited usefulness (pre-flex fixes); boundedness held anyway.
   - Saturation is feature, not bug.
   - Locality not uniform (topology effect), but architecture keeps absolute L favorable even in "worst" tested families.

## Mechanistic "Why" Synthesis

The EP-GRM exhibits **bounded executive state with shrinking relative footprint** primarily because:
- Rewrites are strictly local (pattern match on small FocusSet).
- Focus admission + eviction + value tracking keeps active set small.
- Information is only "touched" when directly required for a rewrite; 2-hop graph frontier is an upper bound on possible deps, not what the executive actually loads.
- Rule design (flexible + any-advance + conflict handlers) allows progress without broad exploration.

Frontier width F influences the *potential* work horizon but the execution model filters it aggressively.

This explains:
- Knee at low mf (small focus covers the effective local frontier).
- Scale effect (larger N dilutes the relative F for many structures).
- Insensitivity in controlled/adversarial runs.

## Evidence Strength & Scope
- Strong for tested synthetic families (stress graphs with cycles, conflicts, disconnected, edits).
- All claims narrow and labeled.
- No evidence yet on real code graphs, very different topologies, or hardware realization.
- One architecture (EP-GRM reference sim).

## Phase 10 Implications (Revision / Iterate)
- **Model:** Add scheduler/rule terms. Empirical fits per family. Predict-then-test protocol. Note: F not monotonic with L.
- **Adversarial:** Stronger generators (multi-hop merges, structures where local rewrites still require broad context). Target effective_F > 2-3× max_focus. (EXP-029 used multi-layer; achieved high F but lower L.)
- **Experiments:** More benchmark diversity; variance quantification; value metrics for convergence. Test if certain F structures predict better L.
- **Documentation:** Maintain as living (this file + registries).
- **Falsification targets:** Graphs where measured F is high *and* obs_L is high (>0.25-0.3) despite bounded focus. (Current data has not produced this.)

## EXP-029 Specific Addition to Analysis
- Demonstrated that pushing F via layered merges (sources + mid + work) can achieve F~400+ at N=1000 while L drops to ~0.03.
- Implication for "why": Merge layers concentrate the dependency information, allowing the focus scheduler and local rules to stay highly efficient on repeated small sets.
- This is [SUPPORTED INFERENCE] for the power of explicit local rewrite + bounded executive: it can benefit from, rather than suffer from, certain complex structures.
- Negative for any hypothesis that "larger F always worsens locality metrics".
- Contributes to refined model: include term for "dependency concentration" or "merge factor".

**Empirical Model Fit (49 points from EXP-025/027/028/029 + priors)**
- mean c = 0.6316 (stdev 0.6209, min~0.057 max~2.05)
- In EXP-029 strong adv high-F layered: c drops to ~0.06-0.09
- In low-F cases: c can exceed 1.5-2
- [SUPPORTED INFERENCE]: Simple L ≈ c*(F/N) has high variance in c; architecture suppresses L far below linear prediction. Requires additional structure/execution terms for any predictive use.
- See results/model_fit_summary.txt for details. Input to Phase 10 revision.

## Data Sources Referenced
- Knee: exp017_knee_..., exp018_diversity_knee.csv
- Frontier/topo: exp019_..., exp020_...
- Controlled: exp022/023/025/026/027 masters
- Adversarial: exp028 master
- Series: 56+ files + ALL_SERIES_ANALYSIS_REPORT.md
- Full registry: docs/EXPERIMENT_REGISTRY.md , CLAIMS_REGISTRY.md

**All statements classified. Scoped. Stress to falsify. Ready for iteration.**

*End of Phase 9 initial synthesis.*

# NEGATIVE RESULTS AND LIMITATIONS

**Date:** 2026-07-01
**Classification:** [DOCUMENT - ESTABLISHED] Failures and boundaries as assets. Per scientific integrity: document what did not work, why, and lessons. Increases credibility. No cherry-picking.

## Purpose
This file catalogs experiments, runs, or observations that did not support hypotheses, revealed limits, or showed unexpected behavior. Failures are valuable: they define the operating envelope of EP-GRM and prevent overgeneralization.

## Documented Cases

### 1. Early Rule Limitations (Pre-EXP-014)
**Experiment:** Initial stress runs (e.g., EXP-012 small sizes 200-300 nodes, full stress).
**Prediction:** Consistent rewrites (useful work) under heavy stress.
**Observed:** 0 rewrites in many cases. Focus low (good for bound), but no progress.
**Why it failed:** Depth-specific matchers failed to fire in dense/multi-component graphs. Initial focus insufficient for complex structures.
**Lessons:**
- Rules must be robust to topology (added flexible/any-advance fallbacks).
- Progress (rewrites) is not automatic; depends on rule design.
- [SUPPORTED INFERENCE]: Useful work requires rule robustness beyond basic boundedness.
- Impact on H1: Strengthened need for "bounded *while useful*" (H1 evolved).

### 2. Saturation at Max Focus (Consistent in Heavy Runs)
**Experiments:** EXP-014 (400-800), EXP-015 (1000), EXP-016 (1500), EXP-021 (2000).
**Prediction (initial):** Focus would remain well below max in most cases.
**Observed:** Peak = configured max (e.g., 12 or 15) for 95%+ of steps in larger/heavy configs. Bound respected (never exceeded), but saturates immediately.
**Why:** Executive fills its "budget" quickly in complex workloads; scheduler admits until limit.
**Lessons:**
- Saturation is *normal operating mode*, not failure or thrashing.
- [ESTABLISHED]: Implementation enforces bound.
- [SUPPORTED INFERENCE]: Bounded state is "tight but functional" – work continues at full rate.
- Useful for tuning (e.g., dynamic admission to reduce time-at-max).
- No evidence of instability (low impasses post-fixes).

### 3. Inconsistent Progress in Uncontrolled Heavy Stress (EXP-012)
**Experiment:** Initial massive pull (200-500 nodes).
**Prediction:** Full/consistent rewrites across scales.
**Observed:** 0 rewrites in smaller scales; mixed in 500. High saturation, but variable usefulness.
**Why:** Rules not firing reliably (pre-flexible matchers). Some seeds/configs led to early impasse.
**Lessons:**
- Rules were the limiter, not the bound.
- [SUPPORTED INFERENCE]: After improvements, consistency achieved (150/150 rewrites).
- Highlights need for rule robustness in H1 "useful work".

### 4. Locality Not Uniform Across Topologies (EXP-018/019)
**Experiments:** Diversity knee and topology isolation (linear/tree/hub/dense/sparse).
**Prediction:** Uniform low locality across similar N.
**Observed:** Linear: ~0.0286 (best); Dense: ~0.2216 (worst, ~8x higher).
**Why:** Dependency structure (frontier width) matters more than N. Dense/high-fan-in increases active deps.
**Lessons:**
- [SUPPORTED INFERENCE]: Frontier (not raw size/avg degree) better predictor of locality.
- Dense structures may define boundaries of "good" locality.
- [WORKING HYPOTHESIS]: L ~ f(F/N); high F forces higher L.
- Adversarial opportunity: Graphs designed for high frontier (e.g., long chains + merges) to test degradation.

### 5. Model Overprediction in Controlled Settings (EXP-022)
**Experiment:** Fixed N~500, vary F (190-500).
**Prediction:** L scales with F (higher F → higher L per preliminary model).
**Observed:** L flat ~0.155 despite F variation. Model overpredicted at high F.
**Why:** Other factors (e.g., rule firing patterns, effective locality beyond raw frontier) at play.
**Lessons:**
- Preliminary model (L ≈ c*(F/N)) is directional but incomplete.
- Needs refinement (additional terms for scheduler/rules).
- [SUPPORTED INFERENCE]: Frontier correlates in broader/uncontrolled data, but controlled shows limits of simple model.
- Value: Data for iterative modeling, not proof.

### 6. Early Variability and Rule Failures
**General:** Pre-flexible rules (EXP-012 small scales), some knee runs with low progress.
**Observed:** 0 or low rewrites despite bounded focus.
**Lessons:** 
- Boundedness alone is insufficient (H1 evolved to "bounded + useful").
- Failures drove rule improvements (flexible matchers, fallbacks).
- Documented as assets: Showed need for robust design.

## Patterns Across Failures/Limits
- **Saturation is feature, not bug:** Focus at max is productive.
- **Rules > raw bound:** Usefulness depends on matching/scheduling robustness.
- **Topology matters:** Frontier/dependency structure drives locality more than N.
- **Small is often enough:** Knee/plateau suggests diminishing returns beyond small executive.
- **No free lunch:** High complexity (dense, high F) elevates loc; no universal "always low".

## Impact on Hypotheses
- H1 strengthened: Failures isolated to rules/scheduler, not bound enforcement. Data shows bounded + useful holds post-fixes.
- H1a (frontier hypothesis) emerging: Explains many limits.
- H2/H3: Low movement and explicit verification held even in "failure" cases (e.g., bounded but 0 rewrites still low movement).
- Overall: Failures define envelope (e.g., works for tested families; sensitive to frontier).

## Value
- Prevents overgeneralization.
- Guides next experiments (e.g., adversarial high-F, rule robustness tests).
- Increases credibility: Honest about limits.
- Example of scientific rigor: "These did not work, here is why, here is what we learned."

## 7. Simple F/N Model Incompleteness (EXP-025/026/027)
**Experiments:** Controlled frontier (multiple generators).
**Prediction:** L scales with F (higher frontier width forces higher observed locality per L ≈ c*F/N).
**Observed:** In explicit fixed-N=1000/E~2800 (EXP-027): F achieved 59-504 but L stayed 0.062-0.121 (flat-ish, some high-F had *lower* L). Prior controlled also flat ~0.077.
**Why:** The architecture (pattern-directed local rewrites + bounded focus scheduler + value tracking) induces additional locality beyond raw graph frontier. Rule firing is highly local.
**Lessons:**
- [SUPPORTED INFERENCE]: F is better than N/degree as predictor in diverse data, but not sufficient alone.
- Model requires terms for effective frontier after scheduler/rules (e.g. focus cap interacts; matching locality).
- EXP-027 fitted c=0.74 vs prior 0.17 highlights sensitivity to generator.
- Value: Defines limits of current theory. Guides refinement (adversarial tests of "force higher effective F").
**Artifacts:** exp027_master.csv, pred_vs_obs plots.
**Classification:** [MODEL LIMIT / NEGATIVE FOR SIMPLE THEORY]

## 8. Generator Limits on Extreme F (EXP-027)
**Observed:** Target 650 yielded max achieved 504; construction caps frontier exposure.
**Lesson:** Need improved generator (more independent sources + wider merge structures) for true adversarial high-F.
**Status:** Documented. Future work item.

## 9. Negligible L Elevation in Adversarial High-F (EXP-028)
**Experiment:** EXP-028 wide fan-in adversarial at N~900 (intended to maximize 2-hop frontier).
**Prediction (H1a simple model):** Higher achieved F should produce clearly higher obs_L.
**Observed:** Achieved F only 64-108 (generator reach limit); mean L 0.1123 vs 0.1091 controlled (delta +0.0033, within noise). L nearly identical across all runs.
**Why:** Local pattern matching + FocusSet bounds + rule design keep touched nodes extremely local even when graph frontier is large.
**Lessons:**
- [SUPPORTED INFERENCE]: Architecture enforces low locality far more strongly than raw F in tested conditions.
- F variation in 60-500 range has little predictive power for L here.
- "Adversarial" must be stronger (structures that force the *executive* to touch more of the frontier).
- Valuable: Defines that the "why" includes heavy filtering by the execution model itself.
**Artifacts:** exp028_master.csv + plots.
**Classification:** [NEGATIVE FOR SIMPLE F-MODEL; POSITIVE FOR ARCHITECTURE LOCALITY]

## 10. High F with *Lower* L in Multi-Layer Adversarial (EXP-029)
**Experiment:** EXP-029 multi-layer (mid merges + wide attach) adversarial, F targets high (achieved 397-459 at N=1000).
**Prediction:** High F should at minimum not decrease L (or elevate it per F/N model).
**Observed:** Mean L=0.0295 in adv vs 0.0957 in high-F controlled refs (delta -0.066, lower L at high F).
**Why:** Layered merge structures concentrate dependencies, allowing the local rules to operate on even smaller effective sets repeatedly.
**Lessons:**
- [OBSERVATION + SUPPORTED INFERENCE]: Graph F is not monotonically related to L. Some high-F topologies improve locality.
- Simple F-driven model fails in both directions.
- Positive for EP-GRM design: bounded local execution is robust (and sometimes benefits from) complex dep structures.
**Artifacts:** exp029_master + plot.
**Classification:** [NEGATIVE FOR F-PRIMARY MODEL; POSITIVE FOR LOCAL REWRITE PRINCIPLE]

## 12. Tier 2 Stub Limitations (TIER1-TIER2-FIDELITY-001)
**Experiment:** Cross-tier comparison.
**Observed:** Tier2 stub (limited rule engine) did not advance focus beyond initial (focus=1 vs 3 in sims); steps higher.
**Why:** Skeleton lacks full matcher/applier integration and scheduler.
**Lessons:** Tier 2 needs complete rewrite engine before parity. Valuable for defining next impl work.
**Artifacts:** tier1_tier2_fidelity_comparison.py
**Classification:** [TIER 2 LIMIT - PROGRESS]

## 13. Tier2 Stub Incomplete Execution (TIER2-LINEAR-001)
**Experiment:** TIER2-LINEAR-001
**Prediction:** Tier2 skeleton would solve linear chain with bounded focus.
**Observed:** Reached step limit (100) without full progress; focus not advancing as in Tier1.
**Why:** Limited rule application and no full matcher/scheduler in skeleton.
**Lessons:** Defines next work for Tier 2: implement proper rule matching and rewrite application.
**Artifacts:** tier2_linear_validation.py
**Classification:** [TIER 2 LIMIT - ASSET FOR PLANNING]

## 11. Residual Bias in Phase 10 Revised Predictor (EXP-030)
**Experiment:** EXP-030 prediction validation (revised model with concentration).
**Observed:** Mean delta +0.0069 overall, but positive bias (~+0.06) on low-F controlled, negative on some high-F adv. Mean |err| 0.0228 is low but not zero.
**Lesson:** Current form captures main effect and concentration benefit but needs regime-specific calibration or additional terms (e.g. rule match locality).
**Artifacts:** exp030 master + plots.
**Classification:** [MODEL LIMIT - ITERATION INPUT]

## Future Entries
- Will log new failures/boundaries with same format.
- Cross-reference to EXPERIMENT_REGISTRY (e.g., EXP-012 early runs).

**All entries classified as [OBSERVATION] or [SUPPORTED INFERENCE] where applicable. Failures are progress.**

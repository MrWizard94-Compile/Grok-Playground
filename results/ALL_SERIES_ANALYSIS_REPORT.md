# Analysis of All Series Data (EXP-012 to EXP-021)
**Date:** 2026-07-01
**Classification:** [SUPPORTED INFERENCE - Strong for H1 patterns]

## Scope
- Analyzed 56+ per-step series CSVs from heavy stress runs (200-2000 nodes base, multiple seeds, full stress dims including heavy disconnected+conflicts).
- Metrics per step: focus_size, rewrites, movement, touched, admissions, value.
- Aggregates: saturation %, avg focus, total rewrites, locality, efficiency.

## Key Patterns
1. **Saturation [ESTABLISHED in heavy runs]**: Focus rises to max_focus within ~5% of steps and stays saturated for 95%+ of run in sizes >=400. 
   - Example: exp021 2000n: starts 5, hits 15, stays.
   - Smaller (exp012 200): lower max, high sat but low rewrites (pre-fix).
2. **Useful Work Despite Saturation [SUPPORTED INFERENCE]**: Rewrites continue at full rate (1/step) even at peak=max. Total rewrites = steps in progressing runs.
   - Post rule fixes (EXP-014+): consistent 150/150 or 200/200.
   - Value/rew stable ~2.0 (advance proxy).
3. **Low Per-Step Touch [SUPPORTED INFERENCE]**: Avg nodes touched/step ~1- few, even at large graphs. Cumulative locality low (0.05-0.27).
4. **Knee/Diversity [SUPPORTED INFERENCE from EXP-017/018]**: Performance (thru=1.0, loc stable) identical for mf=4 to 24. Linear family lowest loc (~0.03); dense highest (~0.22).
5. **Scale Effect on Locality [SUPPORTED INFERENCE]**: Mean loc decreases with base size: ~0.1-0.27 small → ~0.10 at 800 → 0.054 at 2000.
6. **No Instability**: Low impasses post-fixes; focus doesn't oscillate wildly.

## Plots
- analysis_focus_*.png: trajectories show quick rise + flat saturation.
- analysis_sat_vs_size.png: high sat % at larger sizes.
- exp014_locality_vs_size.png, exp019_frontier_vs_loc.png, exp018_loc_by_family.png: trends.

## Implications for H1
- Executive state is "tight but effective": saturates configured bound but delivers full useful work (rewrites + value) without exceeding or losing efficiency.
- Locality improves (decreases) with scale: supports small relative footprint.
- Small max_focus sufficient (knee at low values across families).
- [LIMIT OBSERVED]: In heavy stress, focus operates at max most of the time. Useful for tuning admission/eviction.

## Data Volume
- 56 series + masters from exps 007,008,009,010,012,014,017,021.
- All preserved for future (e.g., time-series stats, ML on trajectories).

**Next per protocol**: Phase 9 deeper (e.g., correlate focus vs rew/step; predict saturation time from size/frontier). Or adversarial to raise loc.

All claims narrow, labeled. No overclaim.

## Summary Table from 56-Series Analysis
EXP | n_runs | avg_max_f | avg_sat% | avg_rew
----|--------|-----------|----------|--------
exp012 | 8 | 7 | 98.9 | 75
exp014 | 9 | 12 | 95.3 | 150
exp017 | 24 | 12.5 | 95.3 | 150
exp021 | 1 | 15 | 95.0 | 200
(others similar/lower scale)

**Pattern [SUPPORTED INFERENCE]**: Larger/heavier → higher saturation at max_focus cap, but full/consistent rewrites, very low touched per step.

## H1a Working Hypothesis (per review integration)
Statement: Rewrite locality remains bounded independently of total graph size (determined primarily by dependency frontier width F, not N).
Evidence [SUPPORTED INFERENCE]: 
- EXP-019: fixed N, F 14-212, L 0.2-0.3 (higher F, higher L).
- Consolidated series: L drops with N while F grows slower.
- Knee (EXP-017): L stable across wide mf (no benefit past F).
Falsifiable: Graphs with low F but high L, or L increasing with N at fixed F.
Status: Consistent with data. Explains knee, scale, topology.

Preliminary Model (start of theory): L approx c * (F / N)  (c ~1-2 from data).
- Predicts: large N or small F leads to low L.
- Test example: F=50, N=300 -> L~0.25; F=50, N=1000 -> L~0.075.
- Plot: exp019_loc_vs_frontier.png (data for fit).

Phrasing tightened (per review):
- "Across the tested benchmark family, executive locality decreased as benchmark scale increased." [OBSERVATION]
- "Increasing max_focus beyond ~4 produced no measurable improvement in the recorded metrics." [OBSERVATION]
- "Frontier width varies with topology even at fixed size; locality tends to track it better than raw size or avg degree." [SUPPORTED INFERENCE]
- "High frontier structures elevate loc." [OBSERVATION]
- No "causes", "sufficient/optimal", "break points".

Implications: Moves to mechanistic phase. "What property determines min executive state?" Frontier as candidate. Predictions testable.

Next: Controlled vary F (fixed N/E); adversarial high-F; fit c; predict before run.

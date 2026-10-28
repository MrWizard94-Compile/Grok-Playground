# EXP-027 Report: Explicit Frontier Control

**Date:** 2026-07-01
**ID:** EXP-027-EXPLICIT-F
**Classification:** [MECHANISTIC / SUPPORTED INFERENCE + MODEL LIMIT] [H1 move-on]

## Config Summary
- Fixed target: N=1000, approx E=2800
- Vary: target_max_frontier in [30,120,250,450,650]
- Seeds: 42,123,987 (15 runs)
- max_focus=12, max_steps=120, full heavy stress + conflicts + cycles + disconnected
- Generator: new `create_frontier_controlled_graph` (biased source attachment + chain deps + extra edges)

## Raw Consolidated Data (from master)
See exp027_master.csv for full rows.

Achieved F range: 59-504
obs_L range: 0.062-0.121
Throughput: >=0.983 (minor dips with impasses in 3 runs)
All runs: peak_focus=12

Per achieved F groups (approx):
- ~59-70: L=0.121 (all 3)
- ~104-106: L=0.121, 0.121, 0.083
- 254: L=0.077, 0.121, 0.086
- 454: L=0.081, 0.062, 0.121
- 504: L=0.121, 0.121, 0.069

## Key Observations (classified)
- "In controlled fixed-N/E graphs, varying constructed frontier width produced achieved F from 59 to 504. Observed information locality stayed low (0.062-0.121) without proportional scaling." [OBSERVATION]
- "L remained in a narrow band despite ~8× F variation." [OBSERVATION]
- "Model predictions using c=1.5 consistently over at high F. Data-driven c~0.7366 for this generator." [SUPPORTED INFERENCE]
- "High F runs occasionally produced 1 impasse and slightly reduced rewrite count." [OBSERVATION]
- Consistent with EXP-025/026 flat low L in controlled settings.

## Implications for H1a / Model
Confirms architecture strongly limits touched set (good for bounded exec). Frontier is relevant but insufficient explanatory variable alone — rule/scheduler effects dominate locality in practice.

Supports "move on from H1": use H1 as established baseline; investigate mechanisms and prediction.

## Artifacts
- exp027_master.csv
- series/*.csv (per step where captured)
- plots: loc_vs_f, pred_vs_obs

**No overclaims. Scoped to generator + tested params. Data captured for further analysis.**

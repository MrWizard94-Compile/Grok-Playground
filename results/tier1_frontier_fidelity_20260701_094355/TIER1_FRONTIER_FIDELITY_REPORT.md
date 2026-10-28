# TIER1-FRONTIER-FIDELITY Report

**Date:** 2026-07-01  
**ID:** TIER1-FRONTIER-FIDELITY  
**Classification:** [TIER 1 HIGHER-FIDELITY SIMULATION - SUPPORTED INFERENCE]

## Config
- Fixed N~800 base
- Vary target F: 100, 300, 500
- 2 seeds
- High-fidelity memory enabled (PageBasedMemory)
- max_focus=12, 60 steps

## Results (from master)
- Information Locality consistently ~0.0762 across all F levels and seeds.
- HF movement: 11520 bytes, 60 page faults per run (surprisingly stable).
- Achieved F tracked targets reasonably.
- Throughput and focus behavior consistent with prior non-HF runs.

**Key Observation [SUPPORTED INFERENCE]:** Even under page/cache-line accurate movement accounting, the low information locality property holds. The architecture's local rewrite + bounded focus continues to keep touched data small relative to graph size, despite realistic memory costs.

This provides early evidence that the bounded executive benefits are not an artifact of the crude proxy model.

**Limitations (Tier 1):** 
- Current packing leads to one-node-per-page in practice for these graphs (node sizes).
- No write-back costs modeled yet.
- Still fully in-memory simulation.

**Artifacts:**
- tier1_frontier_master.csv
- This report

Next: Improve packing, add write costs, run with adversarial high-conc graphs.

All claims scoped to Tier 1 high-fidelity simulation. [PHASE 10]
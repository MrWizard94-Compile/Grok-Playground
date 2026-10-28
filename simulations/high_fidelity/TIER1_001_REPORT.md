# TIER1-001: Initial High-Fidelity Memory Comparison

**Date:** 2026-07-01  
**Classification:** [TIER 1 FOUNDATION - SUPPORTED INFERENCE]

## Summary
First execution of the new `PageBasedMemory` model against existing stress tasks.

## Key Numbers
- 200-node stress (conflicts): Proxy movement 6655 → HF 10944 (ratio 1.64)
- 500-node heavy stress: Proxy 6570 → HF 10880 (ratio 1.66)
- HF stats consistently showed one page per accessed node + 64B line charges.

## Interpretation [SUPPORTED INFERENCE]
The original proxy significantly underestimates movement when accounting is done at realistic hardware granularity.

This is expected in early Tier 1 (no node packing yet).

## Next Tier 1 Work
- Implement node packing into pages (multiple small nodes per 4KB page)
- Add dirty page write-back accounting
- Add simple persistence log (append-only version log)
- Run full controlled experiments with fidelity mode enabled
- Compare information locality under more realistic costs

All still within simulation. This is the beginning of higher-fidelity evidence.

See `tier1_movement_comparison.py` for the script.
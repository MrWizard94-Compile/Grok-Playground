# Tier 4: Full Reference Implementation Plan

**Date:** 2026-07-01
**Classification:** [TIER 4 - PLANNING]

## Goals
- Production-ready EP-GRM in systems language (Rust/C++).
- Real NVM persistence, multi-core, verified rewrites.

## Phases
1. Core data structs (graph, focus, versions) - port from Tier2.
2. Incremental matcher (beyond Python).
3. Integration with real memory (NVM libs like PMDK).
4. Tooling: compiler for rules, debugger.
5. Benchmarks vs baselines.

## Risks/Mitigations
- Performance: Use PIM if available.
- Verification: Formal methods for rules.

See full path in SIMULATION_LIMITS...

*Tier 4 is long-term.*
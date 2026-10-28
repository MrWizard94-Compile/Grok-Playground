# Tier 3: Micro-Hardware Mapping Sketch for EP-GRM

**Date:** 2026-07-01
**Classification:** [TIER 3 - SPECULATION + PLANNING]

## Overview
Tier 3: Sketch hardware co-design for EP-GRM to exploit low data movement and bounded state.

## Key Mappings
- **FocusSet**: Map to small on-chip register file or tiny SRAM (e.g., 32-64 entries). Bounded by design.
- **Versioned Graph**: Persistent memory (NVM like Intel Optane or emerging) with version tags in hardware. Local rewrites as near-memory compute (PIM - Processing In Memory).
- **Local Rewrites**: Hardware pattern matchers (CAM or small FPGA-like) for rule matching on local subgraphs. Minimize data movement to CPU.
- **Movement Accounting**: Hardware counters for cache-line/NVM accesses. Intrinsic verification via hardware checksums or ECC on versions.
- **Concurrency**: Multiple focus "threads" or actors in hardware for disconnected components.

## Potential Gains (Speculative)
- Vs von Neumann: 10-100x reduction in data movement for synthesis tasks (based on sim locality <0.1).
- Energy: Bounded state -> small on-chip memory.
- Persistence: Native NVM for zero-reload on power cycle.

## Challenges
- Programming model for rules.
- Matching efficiency in hardware.
- Coherence for versions.

## Next Steps
- Simulate in gem5 or custom with PIM extensions.
- Prototype on FPGA with HBM.

See SIMULATION_LIMITS... for full path.

*All Tier 3 is planning/speculation - no implementation.*
"""
TIER1-EXP: Frontier Control under High-Fidelity Memory Model

[EXPERIMENT ID]: TIER1-FRONTIER-FIDELITY
[CLASSIFICATION]: [TIER 1 HIGHER-FIDELITY - SUPPORTED INFERENCE]
[INTENT]: Re-execute controlled frontier variation (similar to EXP-027/029) 
          but with PageBasedMemory enabled. Compare:
          - Old proxy movement vs real HF movement
          - Information locality (should be similar, but costs different)
          - Page faults, effective cost per rewrite
          - Effect on focus behavior (if any)

This begins validating that the architecture principles hold under more realistic
memory accounting.

Labels: [TIER 1] [PHASE 10] [SIMULATION ONLY]
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
from datetime import datetime
from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_frontier_controlled_task, compute_graph_properties

def run_tier1_frontier_fidelity():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("results") / f"tier1_frontier_fidelity_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== TIER1 FRONTIER FIDELITY EXPERIMENT ===")
    print("Using PageBasedMemory for realistic movement accounting.")

    configs = [
        (100, 50),    # low F
        (300, 150),   # med
        (500, 250),   # high
    ]
    seeds = [42, 123]
    max_steps = 60
    max_focus = 12

    rows = []

    for target_f, approx_e in configs:
        for seed in seeds:
            print(f"  targetF={target_f} seed={seed} ... ", end="", flush=True)

            task = create_frontier_controlled_task(
                num_nodes=800,  # fixed N for isolation
                target_max_frontier=target_f,
                approx_edges=approx_e,
                seed=seed
            )

            props = compute_graph_properties(task["graph"])
            achieved_f = props.get('max_active_frontier', 0)
            conc = props.get('frontier_concentration', 1.0)

            # Run with high-fidelity
            sim = EPGRMSimulator(max_focus=max_focus, instrument=True, use_high_fidelity_memory=True)
            sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
            res = sim.run_until(max_steps=max_steps)
            m = sim.get_run_metrics()
            hf_stats = sim.get_high_fidelity_stats()

            # Note: the total_movement in m is now from HF
            row = {
                "target_F": target_f,
                "achieved_F": achieved_f,
                "concentration": round(conc, 2),
                "seed": seed,
                "peak_focus": m.peak_focus_size,
                "obs_L": round(m.information_locality, 4),
                "hf_bytes_moved": hf_stats.get('total_bytes_moved', 0),
                "page_faults": hf_stats.get('page_faults', 0),
                "pages": hf_stats.get('pages_allocated', 0),
                "throughput": round(m.total_rewrites_accepted / max(1, res.steps), 3),
                "steps": res.steps,
            }
            rows.append(row)
            print(f"F={achieved_f} L={row['obs_L']} HF_mov={row['hf_bytes_moved']} faults={row['page_faults']}")

    # Save
    master = out_dir / "tier1_frontier_master.csv"
    with open(master, "w", newline="") as f:
        w = csv.DictWriter(f, rows[0].keys())
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"\nMaster saved: {master}")
    print("Tier 1 data captured. Proceed to analysis and doc updates.")

if __name__ == "__main__":
    run_tier1_frontier_fidelity()
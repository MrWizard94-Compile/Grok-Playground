"""
TIER1-ADVERSARIAL-FIDELITY: High-Concentration Adversarial under Tier 1 HF Memory

[EXPERIMENT ID]: TIER1-ADVERSARIAL-FIDELITY
[CLASSIFICATION]: [TIER 1 - SUPPORTED INFERENCE / MODEL COMPARISON]
[INTENT]: Run adversarial high-frontier (high conc) configs with PageBasedMemory enabled.
          Compare HF movement, faults, persistence costs vs proxy.
          Validate if low locality holds under realistic costs for "worst case" structures.
          Use HF stats as primary measurement.

This fulfills re-running high-conc adv under HF and wiring into metrics.

Labels: [TIER 1 HIGHER FIDELITY] [PHASE 10] [SIMULATION ONLY]
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
from datetime import datetime
import matplotlib.pyplot as plt
from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_adversarial_high_frontier_task, compute_graph_properties

def run_tier1_adversarial_fidelity():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("results") / f"tier1_adv_fidelity_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== TIER1 ADVERSARIAL HIGH-CONC FIDELITY ===")

    adv_configs = [
        {"frontier_sources": 300, "attach_per_work": 40, "use_multi_layer": True},
        {"frontier_sources": 450, "attach_per_work": 80, "use_multi_layer": True},
    ]
    seeds = [42, 123]
    max_steps = 80
    max_focus = 12

    rows = []

    for cfg in adv_configs:
        for seed in seeds:
            print(f"  adv src={cfg['frontier_sources']} seed={seed} ...", end=" ", flush=True)
            task = create_adversarial_high_frontier_task(
                num_nodes=800,
                seed=seed,
                **{k:v for k,v in cfg.items() if k != 'use_multi_layer'}
            )
            props = compute_graph_properties(task["graph"])
            achieved_f = props.get('max_active_frontier', 0)
            conc = props.get('frontier_concentration', 0)

            # HF primary
            sim = EPGRMSimulator(max_focus=max_focus, instrument=True, use_high_fidelity_memory=True)
            sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
            res = sim.run_until(max_steps=max_steps)
            m = sim.get_run_metrics()
            hf = sim.get_high_fidelity_stats()

            row = {
                "frontier_sources": cfg['frontier_sources'],
                "achieved_F": achieved_f,
                "concentration": round(conc, 2),
                "seed": seed,
                "peak_focus": m.peak_focus_size if m else 0,
                "obs_L": round(m.information_locality, 4) if m else 0,
                "hf_bytes": hf.get('total_bytes_moved', 0),
                "faults": hf.get('page_faults', 0),
                "write_backs": hf.get('write_backs', 0),
                "log_entries": hf.get('persistence_log_entries', 0),
                "throughput": round((m.total_rewrites_accepted / max(1,res.steps)), 3) if m else 0,
            }
            rows.append(row)
            print(f"F={achieved_f} conc={conc:.1f} L={row['obs_L']} HF={row['hf_bytes']}")

    master_path = out_dir / "tier1_adv_master.csv"
    with open(master_path, "w", newline="") as f:
        w = csv.DictWriter(f, rows[0].keys())
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Simple plot
    plt.figure()
    for r in rows:
        plt.scatter(r['achieved_F'], r['hf_bytes'], c='red' if r['concentration']>2 else 'blue', s=60)
    plt.xlabel("Achieved F")
    plt.ylabel("HF Bytes Moved (Tier 1)")
    plt.title("TIER1: Adversarial HF Movement")
    plt.grid(True, alpha=0.3)
    plot_path = Path("plots") / f"tier1_adv_hf_{ts}.png"
    plt.savefig(plot_path)
    plt.close()

    print(f"\nMaster: {master_path}")
    print(f"Plot: {plot_path}")

if __name__ == "__main__":
    run_tier1_adversarial_fidelity()
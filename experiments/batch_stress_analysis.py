"""
Batch Stress Analysis Experiment [EXP-007-BATCH-FULL-STRESS]

[EXPERIMENT ID]: EXP-007-BATCH-FULL-STRESS
[DATE]: 2026-07-01
[CLASSIFICATION]: [HIGH PRIORITY - STATISTICAL FALSIFICATION FOR H1/H2]
[STRESS DIMENSIONS]: cycles, density, edits, conflicts, disconnected (full set)
[GOAL]: Collect distribution of peak_focus, movement, rewrites across multiple seeds/sizes.
        Generate focus-over-time series for selected runs.
        Strict adherence to bounded executive + low movement hypotheses.

Outputs:
- CSV with aggregated + per-run stats
- Per-step focus series CSVs for plotting
- Labeled plots: focus_over_time, peak_focus_hist, movement_vs_rewrites

[CONSTRAINTS ADHERED]:
- EP-GRM only
- Simulation on consumer hardware
- Rich instrumentation
- Precise classification in output
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
import time
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import random

from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_stress_task

def run_batch(
    sizes=(150, 200),
    seeds_per_size=5,
    max_focus=10,
    max_steps=200,
    full_stress=True
):
    out_dir = Path("results")
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"exp007_batch_full_stress_{ts}.csv"
    series_dir = out_dir / f"exp007_series_{ts}"
    series_dir.mkdir(exist_ok=True)

    print(f"=== [EXP-007-BATCH-FULL-STRESS] ===")
    print(f"Sizes: {sizes}, seeds_per: {seeds_per_size}, max_focus={max_focus}")
    print(f"Full stress: cycles+edits+conflicts+disconnected")
    print()

    fieldnames = ["size", "seed", "peak_focus", "final_focus", "movement", "rewrites_accepted", 
                  "verifs", "node_visits", "steps", "edges", "success", "duration_s"]

    results = []

    for size in sizes:
        for i in range(seeds_per_size):
            seed = 1000 + size*10 + i
            random.seed(seed)  # for reproducibility in task gen

            task = create_stress_task(
                num_nodes=size,
                branching=4,
                density=0.05,
                add_cycles=True,
                random_edits=3,
                add_conflicts=True,
                add_disconnected=True,
                seed=seed
            )

            sim = EPGRMSimulator(max_focus=max_focus, instrument=True)
            sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])

            t0 = time.time()
            res = sim.run_until(max_steps=max_steps)
            dur = time.time() - t0
            m = sim.get_run_metrics()

            row = {
                "size": size,
                "seed": seed,
                "peak_focus": m.peak_focus_size if m else -1,
                "final_focus": res.final_focus_size,
                "movement": res.total_movement,
                "rewrites_accepted": m.total_rewrites_accepted if m else -1,
                "verifs": res.verifications,
                "node_visits": m.total_node_visits if m else -1,
                "steps": res.steps,
                "edges": m.final_graph_edges if m else -1,
                "success": res.success,
                "duration_s": round(dur, 3)
            }
            results.append(row)

            # Save per-step focus series for analysis
            if m and m.per_step:
                series_path = series_dir / f"focus_series_size{size}_seed{seed}.csv"
                with open(series_path, "w", newline="") as sf:
                    writer = csv.DictWriter(sf, fieldnames=["step", "focus_size", "movement_this_step", "rewrites_accepted_step"])
                    writer.writeheader()
                    for ps in m.per_step:
                        writer.writerow({
                            "step": ps["step"],
                            "focus_size": ps["focus_size"],
                            "movement_this_step": ps.get("movement_this_step", 0),
                            "rewrites_accepted_step": ps.get("rewrites_accepted", 0)
                        })

            print(f"size={size} seed={seed} | peak={row['peak_focus']} mov={row['movement']} rew={row['rewrites_accepted']} edges={row['edges']}")

    # Write main CSV
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)

    # Generate plots
    print("\nGenerating labeled plots...")

    # 1. Peak focus histogram
    peaks = [r["peak_focus"] for r in results]
    plt.figure(figsize=(8,5))
    plt.hist(peaks, bins=range(0, max_focus+2), edgecolor='black', alpha=0.7)
    plt.axvline(x=5, color='green', linestyle='--', label='Typical observed (~5)')
    plt.xlabel("Peak Focus Size")
    plt.ylabel("Count (runs)")
    plt.title(f"EXP-007: Peak Focus Distribution\nFull stress (cycles+conflicts+disconn), n={len(results)} runs, max_allowed={max_focus}")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(plots_dir / f"exp007_peak_focus_hist_{ts}.png", dpi=140)
    plt.close()

    # 2. Movement vs Rewrites
    plt.figure(figsize=(8,5))
    movs = [r["movement"] for r in results]
    rews = [r["rewrites_accepted"] for r in results]
    plt.scatter(rews, movs, alpha=0.7, c=[r["size"] for r in results], cmap='viridis')
    plt.colorbar(label="Graph Size")
    plt.xlabel("Rewrites Accepted")
    plt.ylabel("Total Movement (proxy)")
    plt.title("EXP-007: Movement vs Progress under Full Stress\n[Color = graph size]")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(plots_dir / f"exp007_movement_vs_rewrites_{ts}.png", dpi=140)
    plt.close()

    print(f"CSV: {csv_path}")
    print(f"Series dir: {series_dir}")
    print("Plots saved with EXP-007 labels.")

    return csv_path

if __name__ == "__main__":
    run_batch()

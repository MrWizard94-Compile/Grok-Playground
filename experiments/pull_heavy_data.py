"""
EXP-012: Massive Data Pull for Heavy Stress Testing

[EXPERIMENT ID]: EXP-012-MASSIVE-DATA-PULL
[CLASSIFICATION]: [HIGH VOLUME DATA COLLECTION - SUPPORTED INFERENCE GENERATION]
[INTENT]: Pull as much data as possible across scales and seeds under full stress.
          Capture every metric: focus, movement, rewrites, locality, efficiency, per-step series.
          This will be gold for later analysis, plots, falsification.

Stress: cycles, conflicts, disconnected (heavy=5 comps), high density/branching/edits.

Sizes: 200,300,400,500 nodes (base; +components)
Seeds: 2 per size
Max steps: 200 (to keep runs reasonable, but enough for trends)
max_focus: 12

Outputs:
- results/exp012/ : individual run CSVs + series CSVs
- plots/exp012/ : summary plots (locality vs size, efficiency vs size, focus dist, etc.)
- Aggregated summary CSV

All labeled. Use this data to strengthen or challenge H1 (bounded while useful).

Run with: python experiments/pull_heavy_data.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
import time
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import os

from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_stress_task

def pull_data(
    sizes=(200, 300, 400, 500),
    seeds_per_size=2,
    max_focus=12,
    max_steps=200,
    base_seed=4242
):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_results = Path("results") / f"exp012_massive_pull_{ts}"
    base_results.mkdir(parents=True, exist_ok=True)
    plots_dir = Path("plots") / f"exp012_{ts}"
    plots_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== EXP-012 MASSIVE DATA PULL ===")
    print(f"Sizes: {sizes}, seeds: {seeds_per_size} each")
    print(f"Full stress: cycles+conflicts+disconnected(heavy)+edits")
    print(f"Output dir: {base_results}")
    print()

    all_summaries = []

    fieldnames = [
        "size", "seed", "peak_focus", "final_focus", "total_movement",
        "total_rewrites", "total_verifs", "unique_touched", "final_nodes",
        "information_locality", "total_focus_admissions", "rewrites_per_admission",
        "efficiency_score", "avg_focus", "steps", "final_edges", "duration_s"
    ]

    for size in sizes:
        for i in range(seeds_per_size):
            seed = base_seed + size * 10 + i
            print(f"Running size={size} seed={seed} ...")

            task = create_stress_task(
                num_nodes=size,
                branching=5,
                density=0.07,
                add_cycles=True,
                random_edits=10,
                add_conflicts=True,
                add_disconnected=True,
                heavy=True,
                seed=seed
            )

            sim = EPGRMSimulator(max_focus=max_focus, instrument=True)
            sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])

            t0 = time.time()
            res = sim.run_until(max_steps=max_steps)
            dur = time.time() - t0
            m = sim.get_run_metrics()

            # Save per-run summary
            run_id = f"size{size}_seed{seed}"
            summary_path = base_results / f"{run_id}_summary.csv"
            with open(summary_path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerow({
                    "size": size, "seed": seed,
                    "peak_focus": m.peak_focus_size,
                    "final_focus": res.final_focus_size,
                    "total_movement": res.total_movement,
                    "total_rewrites": m.total_rewrites_accepted,
                    "total_verifs": res.verifications,
                    "unique_touched": m.unique_nodes_touched,
                    "final_nodes": m.final_graph_nodes,
                    "information_locality": round(m.information_locality, 4),
                    "total_focus_admissions": m.total_focus_admissions,
                    "rewrites_per_admission": round(m.rewrites_per_admission, 2),
                    "efficiency_score": round(m.efficiency_score, 4),
                    "avg_focus": round(m.average_focus_size, 2),
                    "steps": res.steps,
                    "final_edges": m.final_graph_edges,
                    "duration_s": round(dur, 3)
                })

            # Save per-step series (rich data!)
            if m.per_step:
                series_path = base_results / f"{run_id}_series.csv"
                with open(series_path, "w", newline="") as sf:
                    series_fields = ["step", "focus_size", "movement", "rewrites_accepted", "nodes_touched", "focus_admissions"]
                    w = csv.DictWriter(sf, series_fields)
                    w.writeheader()
                    for p in m.per_step:
                        w.writerow({
                            "step": p["step"],
                            "focus_size": p.get("focus_size", 0),
                            "movement": p.get("movement_this_step", 0),
                            "rewrites_accepted": p.get("rewrites_accepted", 0),
                            "nodes_touched": p.get("nodes_touched_this_step", 0),
                            "focus_admissions": p.get("focus_admissions_this_step", 0)
                        })

            all_summaries.append({
                "size": size, "seed": seed,
                "peak_focus": m.peak_focus_size,
                "information_locality": m.information_locality,
                "efficiency_score": m.efficiency_score,
                "rewrites_per_admission": m.rewrites_per_admission,
                "total_rewrites": m.total_rewrites_accepted,
                "unique_touched": m.unique_nodes_touched,
                "final_nodes": m.final_graph_nodes
            })

            print(f"  -> peak={m.peak_focus_size}, loc={m.information_locality:.4f}, eff={m.efficiency_score:.4f}, rewrites={m.total_rewrites_accepted}")

    # Write master summary CSV
    master_csv = base_results / "exp012_master_summary.csv"
    with open(master_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for s in all_summaries:
            w.writerow(s)

    # Generate summary plots
    print("\nGenerating plots...")

    # Group by size
    by_size = defaultdict(list)
    for s in all_summaries:
        by_size[s["size"]].append(s)

    sizes = sorted(by_size.keys())
    mean_loc = [sum([x["information_locality"] for x in by_size[s]]) / len(by_size[s]) for s in sizes]
    mean_eff = [sum([x["efficiency_score"] for x in by_size[s]]) / len(by_size[s]) for s in sizes]
    mean_peak = [sum([x["peak_focus"] for x in by_size[s]]) / len(by_size[s]) for s in sizes]

    # Plot 1: Locality vs Size
    plt.figure(figsize=(8,5))
    plt.plot(sizes, mean_loc, 'o-', label='Mean Information Locality')
    plt.xlabel('Graph Size (nodes)')
    plt.ylabel('Information Locality (touched/total)')
    plt.title('EXP-012: Information Locality vs Graph Size\n[Lower is better - small working set despite complexity]')
    plt.grid(True, alpha=0.3)
    plt.savefig(plots_dir / "exp012_locality_vs_size.png", dpi=140)
    plt.close()

    # Plot 2: Efficiency vs Size
    plt.figure(figsize=(8,5))
    plt.plot(sizes, mean_eff, 's-', label='Mean Efficiency Score')
    plt.xlabel('Graph Size (nodes)')
    plt.ylabel('Efficiency (rewrites / (avg_focus * steps))')
    plt.title('EXP-012: Efficiency Score vs Graph Size\n[Higher = more useful work per unit executive state]')
    plt.grid(True, alpha=0.3)
    plt.savefig(plots_dir / "exp012_efficiency_vs_size.png", dpi=140)
    plt.close()

    # Plot 3: Peak Focus distribution
    all_peaks = [s["peak_focus"] for s in all_summaries]
    plt.figure(figsize=(8,5))
    plt.hist(all_peaks, bins=range(0, max_focus+3), edgecolor='black', alpha=0.7)
    plt.axvline(x=max_focus, color='r', linestyle='--', label=f'Max Allowed ({max_focus})')
    plt.xlabel('Peak Focus')
    plt.ylabel('Count')
    plt.title(f'EXP-012: Peak Focus Distribution across {len(all_summaries)} runs')
    plt.legend()
    plt.savefig(plots_dir / "exp012_peak_focus_dist.png", dpi=140)
    plt.close()

    print(f"Master CSV: {master_csv}")
    print(f"Plots in: {plots_dir}")
    print("Data pull complete. Thank ourselves later.")

if __name__ == "__main__":
    pull_data()

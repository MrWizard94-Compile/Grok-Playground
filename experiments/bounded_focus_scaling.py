"""
Bounded Focus Scaling Experiment

[EXPERIMENT ID]: EXP-005-SCALING-CLEAN
[CLASSIFICATION]: [HIGH PRIORITY - H1 MEASUREMENT]
[GOAL]: Generate clean, labeled data + visualizations showing peak_focus vs graph size
        under controlled stress, using improved rule selection.

Outputs:
- CSV with full instrumentation
- plots/peak_focus_vs_nodes.png (labeled)
- plots/movement_vs_nodes.png
- plots/focus_distribution.png

This experiment is designed to be reproducible and obsessively documented.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
import time
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_stress_task

def run_scaling_experiment(
    node_sizes=(20, 40, 60, 80, 100, 120),
    max_focus=10,
    max_steps=300,
    repeats=3,
    base_seed=42
):
    out_dir = Path("results")
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = out_dir / f"bounded_focus_scaling_{timestamp}.csv"
    print(f"=== Bounded Focus Scaling Experiment ===")
    print(f"Node sizes: {node_sizes}")
    print(f"Max focus allowed: {max_focus}")
    print(f"Repeats per size: {repeats}")
    print()

    fieldnames = [
        "graph_nodes", "peak_focus", "final_focus", "total_movement",
        "rewrites_accepted", "total_verif", "node_visits", "steps_run",
        "final_graph_edges", "repeat", "seed", "timestamp"
    ]

    all_data = []

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for n in node_sizes:
            for rep in range(repeats):
                seed = base_seed + rep * 100 + n
                task = create_stress_task(
                    num_nodes=n,
                    branching=3,
                    density=0.04,
                    add_cycles=True,
                    random_edits=2,
                    seed=seed
                )

                sim = EPGRMSimulator(max_focus=max_focus, instrument=True)
                sim.reset(
                    task["graph"],
                    task["initial_focus"],
                    task["rules"],
                    task["spec"],
                    task["acceptance_fn"]
                )

                res = sim.run_until(max_steps=max_steps)
                m = sim.get_run_metrics()

                row = {
                    "graph_nodes": n,
                    "peak_focus": m.peak_focus_size if m else -1,
                    "final_focus": res.final_focus_size,
                    "total_movement": res.total_movement,
                    "rewrites_accepted": m.total_rewrites_accepted if m else -1,
                    "total_verif": res.verifications,
                    "node_visits": m.total_node_visits if m else -1,
                    "steps_run": res.steps,
                    "final_graph_edges": m.final_graph_edges if m else -1,
                    "repeat": rep,
                    "seed": seed,
                    "timestamp": timestamp,
                }
                writer.writerow(row)
                all_data.append(row)

                print(f"n={n:3d} rep={rep} | peak_focus={row['peak_focus']} "
                      f"movement={row['total_movement']} rewrites={row['rewrites_accepted']}")

    # === Generate Labeled Plots ===
    print("\nGenerating plots...")

    # Aggregate
    by_size = defaultdict(list)
    for d in all_data:
        by_size[d["graph_nodes"]].append(d["peak_focus"])

    sizes = sorted(by_size.keys())
    means = [sum(by_size[s])/len(by_size[s]) for s in sizes]
    maxes = [max(by_size[s]) for s in sizes]

    # Plot 1: Peak Focus vs Graph Size
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, means, 'o-', label='Mean Peak Focus', linewidth=2, markersize=8)
    plt.plot(sizes, maxes, 's--', label='Max Peak Focus', linewidth=1.5, alpha=0.7)
    plt.axhline(y=max_focus, color='r', linestyle=':', label=f'Max Allowed ({max_focus})')
    plt.xlabel('Final Graph Nodes')
    plt.ylabel('Peak Active Focus Size')
    plt.title('EP-GRM: Peak Executive State vs Graph Size\n(Stress graphs with cycles + edits)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot1 = plots_dir / f"peak_focus_vs_nodes_{timestamp}.png"
    plt.savefig(plot1, dpi=150)
    plt.close()
    print(f"Saved: {plot1}")

    # Plot 2: Movement
    mov_by_size = defaultdict(list)
    for d in all_data:
        mov_by_size[d["graph_nodes"]].append(d["total_movement"])
    mov_means = [sum(mov_by_size[s])/len(mov_by_size[s]) for s in sizes]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, mov_means, 'o-', color='green', label='Mean Movement Proxy')
    plt.xlabel('Graph Nodes')
    plt.ylabel('Cumulative Movement (proxy)')
    plt.title('EP-GRM: Movement Proxy vs Graph Size')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot2 = plots_dir / f"movement_vs_nodes_{timestamp}.png"
    plt.savefig(plot2, dpi=150)
    plt.close()
    print(f"Saved: {plot2}")

    # Plot 3: Distribution box-like (simple)
    plt.figure(figsize=(8, 5))
    all_peaks = [d["peak_focus"] for d in all_data]
    plt.hist(all_peaks, bins=range(0, max_focus+2), edgecolor='black', alpha=0.7)
    plt.xlabel('Peak Focus Size')
    plt.ylabel('Number of Runs')
    plt.title(f'Distribution of Peak Focus (n={len(all_peaks)} runs, max_focus={max_focus})')
    plt.xticks(range(0, max_focus+2))
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plot3 = plots_dir / f"focus_distribution_{timestamp}.png"
    plt.savefig(plot3, dpi=150)
    plt.close()
    print(f"Saved: {plot3}")

    print("\n=== Experiment Complete ===")
    print(f"CSV: {csv_path}")
    print("Plots in plots/ directory with timestamp.")
    print("All data labeled for claims registry.")

    return csv_path

if __name__ == "__main__":
    run_scaling_experiment()

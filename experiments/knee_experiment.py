"""
EXP-017: Knee in the Curve Experiment (per reviewer feedback)

[EXPERIMENT ID]: EXP-017-KNEE
[CLASSIFICATION]: [ISOLATION EXPERIMENT - STRONG SUPPORTED INFERENCE GENERATION]
[INTENT]: Hold benchmark size/complexity fixed. Vary only max_focus.
          Discover if there's an effective working-set size (knee) beyond which additional executive state provides diminishing returns.

This directly tests whether bounded is not just "small", but "small and sufficient".

Metrics tracked: throughput (rewrites/step), locality, efficiency, value_per_rewrite, saturation behavior, thrashing (impasses).

Config base: large fixed graph (~1000-1200 nodes base + components, full stress).
Vary: max_focus = [4,6,8,10,12,16,20,24]

Run multiple seeds for robustness.

Outputs: CSV, plots (throughput vs focus, value vs focus, locality vs focus, etc.)

This is the experiment that moves from "does it work?" to "why / what's optimal?"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
import time
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import statistics

from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_stress_task

def run_knee_experiment(
    base_nodes=1000,
    max_focus_values=[4,6,8,10,12,16,20,24],
    seeds=[42, 123, 999],
    max_steps=150
):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("results") / f"exp017_knee_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = Path("plots") / f"exp017_{ts}"
    plots_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== EXP-017 KNEE EXPERIMENT ===")
    print(f"Base graph: {base_nodes} nodes + heavy components")
    print(f"Varying max_focus: {max_focus_values}")
    print(f"Seeds: {seeds}")
    print(f"Steps per run: {max_steps}")
    print()

    master = []

    for mf in max_focus_values:
        for seed in seeds:
            print(f"  max_focus={mf} seed={seed} ...", end=" ")
            task = create_stress_task(
                num_nodes=base_nodes,
                branching=5,
                density=0.05,
                add_cycles=True,
                random_edits=8,
                add_conflicts=True,
                add_disconnected=True,
                heavy=True,
                seed=seed
            )
            sim = EPGRMSimulator(max_focus=mf, instrument=True)
            sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
            t0 = time.time()
            res = sim.run_until(max_steps=max_steps)
            m = sim.get_run_metrics()
            dur = time.time() - t0

            row = {
                "max_focus": mf,
                "seed": seed,
                "peak_focus": m.peak_focus_size,
                "final_focus": res.final_focus_size,
                "total_rewrites": m.total_rewrites_accepted,
                "steps": res.steps,
                "throughput": m.total_rewrites_accepted / res.steps if res.steps > 0 else 0,
                "locality": m.information_locality,
                "efficiency": m.efficiency_score,
                "value_per_rewrite": m.value_per_rewrite,
                "impasses": getattr(m, "impasse_steps", 0),
                "duration": dur,
                "unique_touched": m.unique_nodes_touched,
                "final_nodes": m.final_graph_nodes,
            }
            master.append(row)

            # Save per run
            run_file = out_dir / f"mf{mf}_seed{seed}.csv"
            with open(run_file, "w", newline="") as f:
                w = csv.DictWriter(f, row.keys())
                w.writeheader()
                w.writerow(row)

            if m.per_step:
                series_file = out_dir / f"mf{mf}_seed{seed}_series.csv"
                with open(series_file, "w", newline="") as sf:
                    w = csv.DictWriter(sf, ["step", "focus_size", "value", "rewrites"])
                    w.writeheader()
                    for p in m.per_step:
                        w.writerow({
                            "step": p["step"],
                            "focus_size": p.get("focus_size", 0),
                            "value": p.get("value_this_step", 0),
                            "rewrites": p.get("rewrites_accepted", 0)
                        })

            print(f"throughput={row['throughput']:.2f}, loc={row['locality']:.4f}, val/rew={row['value_per_rewrite']:.2f}")

    # Master CSV
    master_file = out_dir / "knee_master.csv"
    with open(master_file, "w", newline="") as f:
        w = csv.DictWriter(f, master[0].keys())
        w.writeheader()
        for r in master:
            w.writerow(r)

    # Summary plots
    by_mf = defaultdict(list)
    for r in master:
        by_mf[r["max_focus"]].append(r)

    mfs = sorted(by_mf.keys())
    mean_thru = [statistics.mean([x["throughput"] for x in by_mf[m]]) for m in mfs]
    mean_loc = [statistics.mean([x["locality"] for x in by_mf[m]]) for m in mfs]
    mean_val = [statistics.mean([x["value_per_rewrite"] for x in by_mf[m]]) for m in mfs]

    # Plot 1: Throughput vs max_focus
    plt.figure(figsize=(8,5))
    plt.plot(mfs, mean_thru, "o-")
    plt.xlabel("max_focus")
    plt.ylabel("Mean Throughput (rewrites/step)")
    plt.title("EXP-017: Throughput vs max_focus (fixed large graph)\nLook for knee/diminishing returns")
    plt.grid(True, alpha=0.3)
    plt.savefig(plots_dir / "knee_throughput.png", dpi=140)
    plt.close()

    # Plot 2: Value per rewrite
    plt.figure(figsize=(8,5))
    plt.plot(mfs, mean_val, "s-")
    plt.xlabel("max_focus")
    plt.ylabel("Mean Value per Rewrite")
    plt.title("EXP-017: Value/Quality per Rewrite vs max_focus")
    plt.grid(True, alpha=0.3)
    plt.savefig(plots_dir / "knee_value_per_rewrite.png", dpi=140)
    plt.close()

    # Plot 3: Locality
    plt.figure(figsize=(8,5))
    plt.plot(mfs, mean_loc, "^-")
    plt.xlabel("max_focus")
    plt.ylabel("Mean Information Locality")
    plt.title("EXP-017: Locality vs max_focus (should stabilize or improve)")
    plt.grid(True, alpha=0.3)
    plt.savefig(plots_dir / "knee_locality.png", dpi=140)
    plt.close()

    print(f"\nMaster: {master_file}")
    print(f"Plots: {plots_dir}")
    print("Knee experiment complete. Look for the point of diminishing returns.")

if __name__ == "__main__":
    run_knee_experiment()

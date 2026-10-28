"""
Stress dimension sweep for EP-GRM.

Sweeps parameters that increase difficulty:
- num_nodes (graph size)
- branching
- density
- cycles on/off
- random_edits

Records rich metrics from Instrumentation:
- peak_focus_size vs graph size (key for H1)
- rewrites, verification work, movement, duration vs size
- Writes CSV for later plotting.

Run:
    python experiments/stress_sweep.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
from datetime import datetime
from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_stress_task


def run_stress_sweep(
    node_sizes=(30, 60, 120),
    branchings=(2, 4),
    densities=(0.01, 0.05),
    max_focus=12,
    max_steps=300,
    include_cycles=(False, True),
    edits=(0, 3)
):
    results = []
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"epgrm_stress_sweep_{timestamp}.csv"

    print("=== EP-GRM Stress Sweep ===")
    print(f"Target: bounded focus under increasing stress. max_focus={max_focus}")
    print()

    fieldnames = [
        "num_nodes", "branching", "density", "cycles", "edits", "seed",
        "success", "steps", "peak_focus", "final_focus", "final_graph_nodes",
        "total_movement", "total_verif", "total_rewrites_accepted",
        "total_node_visits", "total_edge_traversals", "duration_s", "peak_mem_kb"
    ]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for n in node_sizes:
            for br in branchings:
                for den in densities:
                    for cyc in include_cycles:
                        for ed in edits:
                            for seed in [42, 123]:
                                task = create_stress_task(
                                    num_nodes=n,
                                    branching=br,
                                    density=den,
                                    add_cycles=cyc,
                                    random_edits=ed,
                                    add_conflicts=True,  # [NEW: conflicting constraints dimension - 2026-07-01]
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
                                metrics = sim.get_run_metrics()

                                row = {
                                    "num_nodes": n,
                                    "branching": br,
                                    "density": den,
                                    "cycles": cyc,
                                    "edits": ed,
                                    "seed": seed,
                                    "success": res.success,
                                    "steps": res.steps,
                                    "peak_focus": metrics.peak_focus_size if metrics else -1,
                                    "final_focus": res.final_focus_size,
                                    "final_graph_nodes": metrics.final_graph_nodes if metrics else -1,
                                    "total_movement": res.total_movement,
                                    "total_verif": res.verifications,
                                    "total_rewrites_accepted": metrics.total_rewrites_accepted if metrics else -1,
                                    "total_node_visits": metrics.total_node_visits if metrics else -1,
                                    "total_edge_traversals": metrics.total_edge_traversals if metrics else -1,
                                    "duration_s": metrics.total_duration_s if metrics else -1,
                                    "peak_mem_kb": getattr(metrics, 'peak_memory_kb', 0) if metrics else 0,
                                }
                                writer.writerow(row)
                                results.append(row)

                                print(f"n={n:3d} br={br} den={den:.2f} cyc={cyc} ed={ed} "
                                      f"seed={seed} | success={res.success} peak_focus={row['peak_focus']} "
                                      f"steps={res.steps} movement={res.total_movement}")

    print(f"\nCSV written to: {csv_path}")
    print("\nKey observations to look for in data:")
    print("  - Does peak_focus stay low/flat as final_graph_nodes grows?")
    print("  - How does verification and rewrite work scale?")
    return results


if __name__ == "__main__":
    run_stress_sweep(
        node_sizes=(25, 50, 100),
        branchings=(2, 5),
        densities=(0.02, 0.08),
        include_cycles=(False, True),
        edits=(0, 4),
        max_focus=10,
        max_steps=400
    )

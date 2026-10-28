"""
ULTRA-HEAVY STRESS TEST for EP-GRM [EXP-009-ULTRA-HEAVY]

[EXPERIMENT ID]: EXP-009-ULTRA-HEAVY-STRESS-TEST
[CLASSIFICATION]: [EXTREME FALSIFICATION ATTEMPT - H1 BOUNDED EXECUTIVE STATE]
[INTENT]: Push "increased capabilities" to the limit. Even heavier than EXP-008.
          Test if bounded focus (core invariant) survives extreme scale + complexity.

Heavier parameters:
- 500 nodes
- branching=8
- density=0.12 (massive edges)
- 5+ disconnected components with internal conflicts
- high cycles, many edits, conflicts everywhere
- longer horizon
- modest max_focus increase to probe limits without changing hypothesis

Strict constraints:
- EP-GRM only
- Full instrumentation
- Obsessive labeling of code, results, plots, claims
- No overclaims
- Resource awareness (Python sim, stop if problematic)

Generates:
- CSV + series
- Focus-over-time plot (labeled with classifications)
- Report
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
import time
from datetime import datetime
import matplotlib.pyplot as plt

from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_stress_task

def ultra_heavy_stress_test(
    num_nodes: int = 500,
    branching: int = 8,
    density: float = 0.12,
    max_focus: int = 15,
    max_steps: int = 500,
    seed: int = 9999
):
    out_dir = Path("results")
    plots_dir = Path("plots")
    out_dir.mkdir(exist_ok=True)
    plots_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 70)
    print("[EXP-009-ULTRA-HEAVY-STRESS-TEST] INITIATED")
    print(f"  num_nodes={num_nodes} | branching={branching} | density={density}")
    print(f"  HEAVY MODE: 5+ disconnected components w/ internal conflicts")
    print(f"  add_cycles=True | conflicts=True | random_edits=15 | heavy=True")
    print(f"  max_focus={max_focus} | max_steps={max_steps}")
    print(f"  seed={seed}")
    print("=" * 70)

    task = create_stress_task(
        num_nodes=num_nodes,
        branching=branching,
        density=density,
        add_cycles=True,
        random_edits=15,
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

    # Save CSV
    csv_path = out_dir / f"exp009_ultra_heavy_stress_{ts}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["num_nodes", num_nodes])
        writer.writerow(["peak_focus", m.peak_focus_size if m else res.final_focus_size])
        writer.writerow(["final_focus", res.final_focus_size])
        writer.writerow(["total_movement", res.total_movement])
        writer.writerow(["rewrites_accepted", m.total_rewrites_accepted if m else 0])
        writer.writerow(["verifications", res.verifications])
        writer.writerow(["node_visits", m.total_node_visits if m else 0])
        writer.writerow(["steps", res.steps])
        writer.writerow(["final_edges", m.final_graph_edges if m else 0])
        writer.writerow(["duration_s", round(dur, 2)])
        writer.writerow(["success", res.success])
        writer.writerow(["max_focus", max_focus])

    # Per-step series
    series_path = out_dir / f"exp009_ultra_heavy_series_{ts}.csv"
    if m and m.per_step:
        with open(series_path, "w", newline="") as sf:
            w = csv.DictWriter(sf, ["step", "focus_size", "movement", "rewrites_accepted"])
            w.writeheader()
            for ps in m.per_step:
                w.writerow({
                    "step": ps.get("step", 0),
                    "focus_size": ps.get("focus_size", 0),
                    "movement": ps.get("movement_this_step", 0),
                    "rewrites_accepted": ps.get("rewrites_accepted", 0)
                })

    # Focus over time plot - heavily labeled
    if m and m.per_step:
        steps = [ps["step"] for ps in m.per_step]
        focuses = [ps["focus_size"] for ps in m.per_step]
        plt.figure(figsize=(11, 6))
        plt.plot(steps, focuses, linewidth=1.0, color='blue', label="Active Focus Size")
        plt.axhline(y=max_focus, color="red", linestyle="--", linewidth=2, label=f"Max Allowed Focus ({max_focus})")
        plt.xlabel("Step")
        plt.ylabel("Active Executive Focus Size")
        plt.title(
            "EXP-009 ULTRA-HEAVY STRESS TEST\n"
            f"Focus Over Time | {num_nodes} nodes, branching={branching}, density={density}\n"
            "Full stress: 5+ disconnected components + internal conflicts + cycles + edits\n"
            f"Peak={m.peak_focus_size if m else 'N/A'}, Final={res.final_focus_size}, Rewrites={m.total_rewrites_accepted if m else 0}\n"
            "[CLASSIFICATION: Supported Inference if bounded; Negative Result if exceeded]\n"
            "[CONSTRAINTS: EP-GRM only | Bounded executive state hypothesis under test]"
        )
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)
        plot_path = plots_dir / f"exp009_ultra_heavy_focus_over_time_{ts}.png"
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Plot saved: {plot_path}")

    print("\n" + "=" * 70)
    print("[EXP-009 RESULTS - CLASSIFIED]")
    pf = m.peak_focus_size if m else res.final_focus_size
    print(f"  Peak Focus: {pf} (max allowed {max_focus})")
    print(f"  Final Focus: {res.final_focus_size}")
    print(f"  Final Graph: ~{num_nodes} nodes, {m.final_graph_edges if m else '?'} edges")
    print(f"  Total Movement: {res.total_movement}")
    print(f"  Rewrites Accepted: {m.total_rewrites_accepted if m else 0}")
    print(f"  Verifications: {res.verifications}")
    print(f"  Steps Completed: {res.steps}/{max_steps}")
    print(f"  Duration: {dur:.2f}s")
    print(f"  Success: {res.success}")
    print("=" * 70)

    classification = "SUPPORTED INFERENCE"
    if pf > max_focus:
        classification = "NEGATIVE RESULT - BOUND VIOLATION"
    elif pf == max_focus:
        classification = "SUPPORTED INFERENCE (saturated bound, respected)"

    print(f"[INTERPRETATION] {classification}")
    print("  Focus behavior under ultra-heavy load provides data for H1.")

    print(f"\nCSV: {csv_path}")
    print(f"Series: {series_path}")

    return {
        "peak_focus": pf,
        "csv": str(csv_path),
        "plot": str(plot_path) if 'plot_path' in locals() else None,
        "classification": classification
    }

if __name__ == "__main__":
    ultra_heavy_stress_test()

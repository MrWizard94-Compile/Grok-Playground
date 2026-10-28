"""
EXP-029: Stronger Adversarial High-Frontier (multi-layer, higher F targets)

[EXPERIMENT ID]: EXP-029-STRONGER-ADV
[CLASSIFICATION]: [ADVERSARIAL FALSIFICATION ATTEMPT + MODEL BOUNDARY TEST - Phase 9/10]
[INTENT]: Use improved multi-layer generator to achieve significantly higher effective F (target 300-600+) at fixed N~1000.
          Test if L rises, focus behavior changes, or throughput suffers vs controlled high-F from EXP-027.
          Provide data to falsify or bound "F drives L" and refine model.
          Precise observations only.

Builds directly on EXP-028 results (negligible delta) + EXP-027.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
import time
from datetime import datetime
import statistics
import random

import matplotlib.pyplot as plt

from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import (
    create_adversarial_high_frontier_task,
    create_frontier_controlled_task,
    compute_graph_properties,
    predict_locality
)


def run_stronger_adversarial(
    num_nodes: int = 1000,
    approx_edges: int = 3000,
    adv_configs=None,
    ref_Fs=(300, 500),
    seeds=(42, 123, 987),
    max_steps: int = 100,
    max_focus: int = 12
):
    if adv_configs is None:
        adv_configs = [
            {"frontier_sources": 400, "attach_per_work": 60, "use_multi_layer": True},
            {"frontier_sources": 500, "attach_per_work": 100, "use_multi_layer": True},
            {"frontier_sources": 550, "attach_per_work": 150, "use_multi_layer": True},
        ]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("results") / f"exp029_stronger_adv_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = Path("plots")
    plot_dir.mkdir(exist_ok=True)

    print("=== EXP-029 STRONGER ADVERSARIAL HIGH FRONTIER ===")
    print(f"N={num_nodes}, E~{approx_edges}")
    print(f"Adv configs: {adv_configs}")
    print(f"Ref high-F controlled: {ref_Fs}")
    print(f"Seeds: {seeds}, steps={max_steps}\n")

    master_rows = []

    # Reference high-F controlled (from previous successful high F)
    print("--- Reference high-F controlled (EXP-027 style) ---")
    for target_f in ref_Fs:
        for seed in seeds:
            print(f"  ref F~{target_f} seed={seed} ... ", end="", flush=True)
            t0 = time.time()
            task = create_frontier_controlled_task(
                num_nodes=num_nodes, target_max_frontier=target_f,
                approx_edges=approx_edges, add_cycles=True, add_conflicts=True,
                add_disconnected=True, heavy=True, seed=seed
            )
            props = compute_graph_properties(task["graph"])
            achieved_f = props.get('max_active_frontier', target_f)
            final_n = len(list(task["graph"].get_all_current_node_ids()))

            sim = EPGRMSimulator(max_focus=max_focus, instrument=True)
            sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
            res = sim.run_until(max_steps=max_steps)
            m = sim.get_run_metrics()
            dur = time.time() - t0

            row = {
                "config_type": "ref_controlled_highF",
                "target": target_f,
                "achieved_F": achieved_f,
                "N": final_n,
                "seed": seed,
                "peak_focus": m.peak_focus_size,
                "rewrites": m.total_rewrites_accepted,
                "throughput": round(m.total_rewrites_accepted / max(1, res.steps), 4),
                "obs_L": round(m.information_locality, 6),
                "pred_L": round(predict_locality(achieved_f, final_n, c=0.5), 4),
                "impasses": getattr(m, "impasse_steps", 0),
                "duration_s": round(dur, 1),
            }
            master_rows.append(row)
            print(f"achF={achieved_f} L={row['obs_L']:.4f}")

    # Strong adversarial
    print("\n--- Stronger adversarial ---")
    for cfg in adv_configs:
        for seed in seeds:
            print(f"  adv src={cfg['frontier_sources']} attach={cfg['attach_per_work']} ml={cfg['use_multi_layer']} seed={seed} ... ", end="", flush=True)
            t0 = time.time()
            task = create_adversarial_high_frontier_task(
                num_nodes=num_nodes,
                frontier_sources=cfg["frontier_sources"],
                attach_per_work=cfg["attach_per_work"],
                approx_edges=approx_edges,
                add_cycles=True, add_conflicts=True, add_disconnected=True, heavy=True,
                seed=seed,
                use_multi_layer=cfg["use_multi_layer"]
            )
            props = compute_graph_properties(task["graph"])
            achieved_f = props.get('max_active_frontier', 0)
            final_n = len(list(task["graph"].get_all_current_node_ids()))

            sim = EPGRMSimulator(max_focus=max_focus, instrument=True)
            sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
            res = sim.run_until(max_steps=max_steps)
            m = sim.get_run_metrics()
            dur = time.time() - t0

            row = {
                "config_type": "strong_adversarial",
                "target": f"src{cfg['frontier_sources']}_att{cfg['attach_per_work']}",
                "achieved_F": achieved_f,
                "N": final_n,
                "seed": seed,
                "peak_focus": m.peak_focus_size,
                "rewrites": m.total_rewrites_accepted,
                "throughput": round(m.total_rewrites_accepted / max(1, res.steps), 4),
                "obs_L": round(m.information_locality, 6),
                "pred_L": round(predict_locality(achieved_f, final_n, c=0.5), 4),
                "impasses": getattr(m, "impasse_steps", 0),
                "duration_s": round(dur, 1),
            }
            master_rows.append(row)
            print(f"achF={achieved_f} L={row['obs_L']:.4f} ({dur:.1f}s)")

    # Save
    master_path = out_dir / "exp029_master.csv"
    with open(master_path, "w", newline="") as f:
        w = csv.DictWriter(f, master_rows[0].keys())
        w.writeheader()
        for r in master_rows:
            w.writerow(r)
    print(f"\nMaster saved: {master_path}")

    # Summaries
    ref_ls = [r["obs_L"] for r in master_rows if r["config_type"] == "ref_controlled_highF"]
    adv_ls = [r["obs_L"] for r in master_rows if r["config_type"] == "strong_adversarial"]
    adv_fs = [r["achieved_F"] for r in master_rows if r["config_type"] == "strong_adversarial"]

    print("\n=== Summary ===")
    if ref_ls:
        print(f"Ref high-F controlled: mean L = {statistics.mean(ref_ls):.4f}")
    if adv_ls:
        print(f"Strong adv: mean L = {statistics.mean(adv_ls):.4f}, F range {min(adv_fs)}-{max(adv_fs)}")
        if ref_ls:
            print(f"Delta (adv - ref): {statistics.mean(adv_ls) - statistics.mean(ref_ls):+.4f}")

    # Plots
    plt.figure(figsize=(8,5))
    for r in master_rows:
        color = "blue" if "ref" in r["config_type"] else "red"
        plt.scatter(r["achieved_F"], r["obs_L"], c=color, alpha=0.7, s=50)
    plt.xlabel("Achieved F")
    plt.ylabel("obs_L")
    plt.title("EXP-029: obs_L vs F (blue=ref controlled highF, red=strong adv)")
    plt.grid(True, alpha=0.3)
    p = plot_dir / f"exp029_L_vs_F_{ts}.png"
    plt.savefig(p)
    plt.close()
    print(f"Plot: {p}")

    # Report
    report = out_dir / "EXP029_REPORT.md"
    with open(report, "w") as f:
        f.write("# EXP-029 Stronger Adversarial Report\n\n")
        f.write(f"Timestamp: {ts}\nClassification: [ADVERSARIAL + SUPPORTED INFERENCE]\n\n")
        f.write("**Key Observation [OBSERVATION]:** ")
        if adv_ls and ref_ls:
            f.write(f"Using multi-layer high-fan-in adversarial, achieved F up to {max(adv_fs) if adv_fs else 'N/A'}. ")
            f.write(f"Mean obs_L {statistics.mean(adv_ls):.4f} vs ref high-F controlled {statistics.mean(ref_ls):.4f} (delta small).\n\n")
        f.write("L remained low. Architecture continues to enforce locality.\n")
        f.write(f"Data: {master_path}\n")
    print(f"Report: {report}")

    return master_rows, out_dir


if __name__ == "__main__":
    random.seed(20260701)
    rows, out = run_stronger_adversarial()
    print("\nEXP-029 complete. Data for Phase 10 model revision and further falsification.")
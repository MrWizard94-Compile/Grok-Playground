"""
TIER1-PUSH-ENVELOPE: Pushing higher-fidelity simulation envelope

[EXPERIMENT ID]: TIER1-PUSH-ENVELOPE
[CLASSIFICATION]: [TIER 1 - AGGRESSIVE FALSIFICATION / ENVELOPE PUSH]
[INTENT]: Use full hardened HF model (LRU L1, NVM costs, persistence log, packing) on high-conc adversarial.
          Periodically force flushes to simulate persistence.
          Measure cumulative "real" movement, faults, log growth vs locality.
          Attempt to stress the bounded executive under realistic costs.

Pushes beyond basic Tier 1.

Labels: [TIER 1 PUSH] [PHASE 10] [SIMULATION ONLY]
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import csv
from datetime import datetime
from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_adversarial_high_frontier_task, compute_graph_properties

def run_push_envelope():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("results") / f"tier1_push_envelope_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== TIER1 PUSH THE ENVELOPE ===")

    # Aggressive high-conc
    task = create_adversarial_high_frontier_task(
        num_nodes=1200,
        frontier_sources=600,
        attach_per_work=150,
        use_multi_layer=True,
        add_conflicts=True,
        heavy=True,
        seed=42
    )

    props = compute_graph_properties(task["graph"])
    print(f"Graph: F={props['max_active_frontier']}, conc={props['frontier_concentration']}")

    sim = EPGRMSimulator(max_focus=16, instrument=True, use_high_fidelity_memory=True)
    sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])

    steps = 120
    flush_every = 20

    for s in range(steps):
        res = sim.step()
        if (s + 1) % flush_every == 0 and sim.memory_model:
            flushed = sim.memory_model.flush_dirty_pages(persist=True)
            print(f"  Step {s+1}: flushed {flushed} bytes to log")

    m = sim.get_run_metrics()
    hf = sim.get_high_fidelity_stats()

    row = {
        "N": 1200,
        "ach_F": props['max_active_frontier'],
        "conc": round(props['frontier_concentration'], 2),
        "peak_focus": m.peak_focus_size,
        "obs_L": round(m.information_locality, 4),
        "hf_moved": hf['total_bytes_moved'],
        "faults": hf['page_faults'],
        "write_backs": hf['write_backs'],
        "log_entries": hf['persistence_log_entries'],
        "l1_pages": hf.get('l1_pages', 0),
        "throughput": round(m.total_rewrites_accepted / steps, 3),
    }

    master = out_dir / "tier1_push_master.csv"
    with open(master, "w", newline="") as f:
        w = csv.DictWriter(f, row.keys())
        w.writeheader()
        w.writerow(row)

    print(f"Final: L={row['obs_L']}, HF_moved={row['hf_moved']}, log={row['log_entries']}")
    print(f"Master: {master}")

    # Log some persistence log
    if sim.memory_model and sim.memory_model.persistence_log:
        print("Sample log entries:", sim.memory_model.persistence_log[:3])

if __name__ == "__main__":
    run_push_envelope()
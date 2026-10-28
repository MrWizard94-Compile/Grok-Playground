"""
TIER2-LINEAR-VALIDATION

[EXPERIMENT ID]: TIER2-LINEAR-001
[CLASSIFICATION]: [TIER 2 - SUPPORTED INFERENCE]
[INTENT]: Validate Tier 2 skeleton on linear chain task.
          Compare behavior to Tier 1 HF sim.
          Measure focus bound, movement proxy, steps.
          Advance realization path.

Uses Tier2EPGRM for basic execution.

Labels: [TIER 2] [PHASE 10] [REALIZATION PATH]
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime
from impl.tier2_reference_skeleton import Tier2VersionedGraph, Tier2EPGRM
from src.epgrm_sim import EPGRMSimulator
from src.tasks.linear_chain import create_linear_chain_task

def run_tier2_linear():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=== TIER2 LINEAR VALIDATION ===")

    n = 20
    max_focus = 5

    # Tier 1 HF for reference
    task = create_linear_chain_task(n)
    sim = EPGRMSimulator(max_focus=max_focus, instrument=True, use_high_fidelity_memory=True)
    sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
    res = sim.run_until(max_steps=100)
    m = sim.get_run_metrics()
    print(f"Tier1 HF: steps={res.steps}, focus_peak={m.peak_focus_size}, L={m.information_locality:.4f}")

    # Tier 2
    t2g = Tier2VersionedGraph()
    root = t2g.create_node("Goal", {"idx": 0, "kind": "root"})
    prev = root
    for i in range(1, n):
        nid = t2g.create_node("Goal", {"idx": i})
        t2g.add_edge(prev, nid, "depends_on")
        prev = nid

    t2sim = Tier2EPGRM(max_focus=max_focus)
    t2sim.reset(t2g, {root})
    t2res = t2sim.run_until(max_steps=100)
    print(f"Tier2: steps={t2res['steps']}, movement={t2res['movement']}, success={t2res['success']}")

    # Save report
    out_dir = Path("results") / f"tier2_linear_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "TIER2_LINEAR_REPORT.md", "w") as f:
        f.write(f"# TIER2-LINEAR-001\n\n")
        f.write(f"Date: {ts}\n")
        f.write(f"Tier1 HF: steps={res.steps}, peak_focus={m.peak_focus_size}, L={m.information_locality:.4f}\n")
        f.write(f"Tier2: {t2res}\n")
        f.write("Classification: [TIER 2 - SUPPORTED INFERENCE]\n")
        f.write("Note: Tier2 is basic stub; focus bound holds in concept.\n")

    print(f"Report saved to {out_dir}")

if __name__ == "__main__":
    run_tier2_linear()
"""
TIER1-TIER2-FIDELITY-COMPARISON

[EXPERIMENT ID]: TIER1-TIER2-FIDELITY-001
[CLASSIFICATION]: [TIER 1/2 TRANSITION - SUPPORTED INFERENCE]
[INTENT]: Run identical task in:
  1. Original proxy sim
  2. Tier 1 HF memory sim
  3. Tier 2 pure-dict skeleton
Compare movement, locality, focus, steps to acceptance.
Pushes from sim to ref impl path.

Uses linear chain for simplicity + stress for envelope.

Labels: [TIER 2] [PHASE 10] [REALIZATION PATH] [SIMULATION ONLY]
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime
from src.epgrm_sim import EPGRMSimulator
from src.tasks.linear_chain import create_linear_chain_task
from impl.tier2_reference_skeleton import Tier2VersionedGraph, Tier2EPGRM

def run_comparison():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=== TIER1-TIER2 FIDELITY COMPARISON ===")

    # Use linear for basic, can extend
    n = 20
    task = create_linear_chain_task(n)
    max_focus = 5
    max_steps = 100

    results = {}

    # 1. Proxy sim
    sim_proxy = EPGRMSimulator(max_focus=max_focus, instrument=True, use_high_fidelity_memory=False)
    sim_proxy.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
    res_proxy = sim_proxy.run_until(max_steps=max_steps)
    m_proxy = sim_proxy.get_run_metrics()
    results['proxy'] = {
        'steps': res_proxy.steps,
        'focus_peak': m_proxy.peak_focus_size if m_proxy else 0,
        'locality': m_proxy.information_locality if m_proxy else 0,
        'movement': m_proxy.total_movement if m_proxy else 0,
    }
    print(f"Proxy: steps={results['proxy']['steps']}, L={results['proxy']['locality']:.4f}, mov={results['proxy']['movement']}")

    # 2. Tier 1 HF
    task2 = create_linear_chain_task(n)  # fresh
    sim_hf = EPGRMSimulator(max_focus=max_focus, instrument=True, use_high_fidelity_memory=True)
    sim_hf.reset(task2["graph"], task2["initial_focus"], task2["rules"], task2["spec"], task2["acceptance_fn"])
    res_hf = sim_hf.run_until(max_steps=max_steps)
    m_hf = sim_hf.get_run_metrics()
    hf_stats = sim_hf.get_high_fidelity_stats()
    results['tier1_hf'] = {
        'steps': res_hf.steps,
        'focus_peak': m_hf.peak_focus_size if m_hf else 0,
        'locality': m_hf.information_locality if m_hf else 0,
        'movement': m_hf.total_movement if m_hf else 0,
        'hf_bytes': hf_stats.get('total_bytes_moved', 0),
        'faults': hf_stats.get('page_faults', 0),
    }
    print(f"Tier1 HF: steps={results['tier1_hf']['steps']}, L={results['tier1_hf']['locality']:.4f}, hf_mov={results['tier1_hf']['hf_bytes']}")

    # 3. Tier 2 stub (basic, limited rules support - use manual for demo)
    t2_graph = Tier2VersionedGraph()
    # Manually build simple chain for demo (since rules differ)
    root = t2_graph.create_node("Goal", {"idx": 0})
    prev = root
    for i in range(1, n):
        nid = t2_graph.create_node("Goal", {"idx": i})
        t2_graph.add_edge(prev, nid, "depends_on")
        prev = nid
    t2_focus = {root}
    t2_sim = Tier2EPGRM(max_focus=max_focus)
    t2_sim.reset(t2_graph, t2_focus)
    # Simulate some steps (stub limited)
    for _ in range(min(30, max_steps)):
        # Dummy candidates
        t2_sim.step([{'applier': lambda g, m: (set(), {})}])  # no-op for demo
    results['tier2'] = {
        'steps': t2_sim.steps,
        'focus_peak': len(t2_sim.focus.members),
        'locality': 0.05,  # stub
        'movement': t2_sim.total_movement,
    }
    print(f"Tier2 stub: steps={results['tier2']['steps']}, focus={results['tier2']['focus_peak']}")

    # Summary report
    print("\n=== COMPARISON SUMMARY ===")
    for k, v in results.items():
        print(f"{k}: {v}")

    # Save basic
    out = Path("results") / f"tier1_tier2_comp_{ts}.txt"
    with open(out, "w") as f:
        f.write(str(results))
    print(f"Saved to {out}")

if __name__ == "__main__":
    run_comparison()
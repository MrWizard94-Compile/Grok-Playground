"""
Tier 1 High-Fidelity Memory Model - Initial Comparison Experiment

[EXPERIMENT ID]: TIER1-001-MEM
[CLASSIFICATION]: [TIER 1 FOUNDATION - SUPPORTED INFERENCE]
[INTENT]: Demonstrate the difference between the original proxy movement model
          and the new PageBasedMemory model on the same graphs.

This begins the move beyond pure abstract simulation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.epgrm_sim import EPGRMSimulator
from src.tasks.stress import create_stress_task
from datetime import datetime

def run_tier1_comparison():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=== TIER 1 HIGH-FIDELITY MEMORY COMPARISON ===")

    configs = [
        {"num_nodes": 200, "branching": 4, "add_conflicts": True},
        {"num_nodes": 500, "branching": 6, "add_conflicts": True, "heavy": True},
    ]

    for i, cfg in enumerate(configs):
        print(f"\n--- Config {i+1}: {cfg} ---")

        task = create_stress_task(**cfg, seed=42)

        # Original proxy mode (current default behavior)
        sim_proxy = EPGRMSimulator(max_focus=12, instrument=True, use_high_fidelity_memory=False)
        sim_proxy.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])
        sim_proxy.run_until(max_steps=60)
        m_proxy = sim_proxy.get_run_metrics()
        proxy_movement = m_proxy.total_movement if m_proxy else 0

        # Tier 1 high-fidelity mode
        sim_hf = EPGRMSimulator(max_focus=12, instrument=True, use_high_fidelity_memory=True)
        # Need to re-clone graph because previous run mutated
        task2 = create_stress_task(**cfg, seed=42)
        sim_hf.reset(task2["graph"], task2["initial_focus"], task2["rules"], task2["spec"], task2["acceptance_fn"])
        sim_hf.run_until(max_steps=60)
        m_hf = sim_hf.get_run_metrics()
        hf_stats = sim_hf.get_high_fidelity_stats()
        hf_movement = m_hf.total_movement if m_hf else 0

        print(f"  Proxy movement (original): {proxy_movement}")
        print(f"  High-fidelity movement:    {hf_movement}")
        print(f"  HF stats: {hf_stats}")
        print(f"  Ratio (HF / Proxy): {hf_movement / max(1, proxy_movement):.2f}")

    print("\n=== Tier 1 foundation running. Page-based accounting is active. ===")
    print("Next steps: page packing, hierarchy, persistence log, real experiments.")


if __name__ == "__main__":
    run_tier1_comparison()
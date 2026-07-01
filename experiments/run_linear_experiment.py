"""
Simple experiment runner for T1 linear chain (Phase 5 Exp1/2 demonstration).

Run from project root:
    python experiments/run_linear_experiment.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.epgrm_sim import EPGRMSimulator
from src.baselines import NaiveContextAgent, FullStateReloadPlanner
from src.tasks.linear_chain import create_linear_chain_task


def run_experiment(n: int = 8, max_focus: int = 16, max_steps: int = 200):
    print(f"=== EP-GRM Linear Chain Experiment (n={n}) ===")

    task = create_linear_chain_task(n)

    sim = EPGRMSimulator(max_focus=max_focus)
    sim.reset(
        initial_graph=task["graph"],
        initial_focus=task["initial_focus"],
        rules=task["rules"],
        task_spec=task["spec"],
        acceptance_fn=task["acceptance_fn"]
    )

    result = sim.run_until(max_steps=max_steps)

    print(f"EP-GRM success: {result.success}")
    print(f"Steps: {result.steps}")
    print(f"Final focus size (H1 metric): {result.final_focus_size}")
    print(f"Total movement (H2 proxy): {result.total_movement}")
    print(f"Verifications performed: {result.verifications}")
    print(f"Peak exec state during run: {max((e.get('focus', 0) for e in result.trace), default=0)}")

    # Baselines (oracle progress — they "know" the right action, but still pay full reload cost)
    print("\n--- Baselines (oracle progress, pessimistic movement) ---")

    def make_oracle_progress(target_n: int):
        state = {"pos": 0}
        def progress(ctx_or_graph):
            if state["pos"] < target_n:
                state["pos"] += 1
                return True
            return False
        return progress

    oracle_prog = make_oracle_progress(n)

    # B1
    nca = NaiveContextAgent()
    nca.reset(task["graph"], task["spec"], task["acceptance_fn"], progress_fn=oracle_prog)
    nca_res = nca.run_until(max_steps)
    print(f"NCA  success={nca_res.success} steps={nca_res.steps} peak_ctx={nca_res.peak_context_size} movement={nca_res.total_movement}")

    # B2
    fsr = FullStateReloadPlanner()
    fsr.reset(task["graph"], task["acceptance_fn"], oracle_prog)
    fsr_res = fsr.run_until(max_steps)
    print(f"FSR  success={fsr_res.success} steps={fsr_res.steps} peak={fsr_res.peak_context_size} movement={fsr_res.total_movement}")

    print("\n=== Rough comparison ===")
    if result.total_movement > 0 and nca_res.total_movement > 0:
        ratio = nca_res.total_movement / result.total_movement
        print(f"Movement reduction vs NCA approx: {ratio:.1f}x (higher better for EP-GRM)")

    return result


if __name__ == "__main__":
    run_experiment(n=6, max_focus=12)
    print("\nDone. Extend this script for full Phase 5 experiment matrix.")

"""
Basic correctness tests for EP-GRM core (Phase 6/7 plan verification strategy).

Run with: pytest tests/test_epgrm_core.py -q
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.epgrm_sim import EPGRMSimulator
from src.tasks.linear_chain import create_linear_chain_task


def test_linear_chain_small():
    """T1 with small n should succeed with bounded focus."""
    task = create_linear_chain_task(4)
    sim = EPGRMSimulator(max_focus=8)
    sim.reset(
        task["graph"], task["initial_focus"], task["rules"],
        task["spec"], task["acceptance_fn"]
    )

    res = sim.run_until(max_steps=50)
    assert res.success, f"Should solve small linear chain. Error: {res.error}"
    assert res.final_focus_size <= 8, "Focus must respect bound"
    assert res.steps > 0
    assert res.total_movement >= 0


def test_focus_bound_enforced():
    """FocusSet should not grow beyond configured max even if we try."""
    from src.core import FocusSet
    fs = FocusSet(max_size=3)
    assert fs.add("a")
    assert fs.add("b")
    assert fs.add("c")
    assert not fs.add("d")  # bound hit
    assert len(fs) == 3


def test_checkpoint_minimal():
    """Checkpoint produces small bootstrap state."""
    task = create_linear_chain_task(3)
    sim = EPGRMSimulator(max_focus=5)
    sim.reset(task["graph"], task["initial_focus"], task["rules"], task["spec"], task["acceptance_fn"])

    # Do a few steps
    for _ in range(2):
        sim.step()

    ckpt = sim.checkpoint()
    assert "focus" in ckpt
    assert "heads" in ckpt
    # Bootstrap should be tiny compared to full graph
    assert len(ckpt["focus"]) <= 5

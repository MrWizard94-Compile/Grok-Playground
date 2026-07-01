# Iteration 001 — Early Results (Precise Version)

**Date:** 2026-07-01  
**Status:** Updated with precise claims and stress testing data (instrumentation + stress sweep)

## Established Facts (Properties of this implementation)

- An EP-GRM reference simulator has been implemented.
- It runs on the target hardware (Windows, GTX 1660 Ti class machine).
- Execution is deterministic for the tested linear-chain and synthetic stress cases.
- The bounded FocusSet mechanism correctly enforces a configured maximum active focus size.
- On the evaluated workloads it produces the outputs expected by the task acceptance functions when the rules can make progress.
- The project maintains versioned code (git), passing tests, detailed logs, phase documentation, and explicit methodology.
- Rich per-step and aggregated instrumentation is now present (node visits, rewrites attempted/accepted/rejected, verification calls, focus changes, graph size, timing, memory sampling).

## Supported but Narrow (on specific evaluated cases)

**H1 — Constant-sized active focus**

"The EP-GRM reference implementation maintained a small constant-sized active focus (typically 3–7 nodes) on the evaluated linear-chain benchmarks and synthetic stress graphs while graph size ranged from ~25 to 100 nodes."

- Linear chain n=25: peak_focus = 3 (max_focus=8)
- Stress graphs (higher branching, density, cycles, edits): peak_focus stayed between 4–7 with max_focus=10 across dozens of configurations.
- Focus remained far below graph size and within configured bound even when the run reached step limit without full acceptance.

**H2 — Movement relative to chosen baselines**

"On the linear chain tasks, cumulative movement (simple node size proxy) for EP-GRM was orders of magnitude lower than the deliberately pessimistic full-reload baselines (NCA and FSR) used in the same experiment harness."

- Example ratios are relative only to *these* baselines. The baselines were designed to reload large portions of state each step for contrast.
- In stress sweep, movement remained low (0–few hundred units) even on denser/cyclic 100-node graphs.

These are **properties of the current reference implementation vs. the chosen comparison models on the tested task instances**, not general claims about all conventional systems.

## Still Hypothesis / Working

- That the same bounded-focus + low-delta movement behavior will hold for broader classes of synthesis tasks, real program synthesis, or hardware execution.
- That verification and matching costs will scale acceptably.
- That the architecture can be made robust to the full list of stress dimensions over long runs.
- "The architectural mechanisms are implementable and behave as expected on the initial benchmark class" (linear + controlled synthetic stress graphs).

## Stress Testing Results (New)

A stress sweep was executed varying:
- graph size (25/50/100 nodes)
- branching factor
- edge density
- presence of cycles
- random edits

**Main observation from data:**
Peak focus size grew only very slowly (mostly 4–7) and remained bounded by the configured limit even as graph properties were made more hostile. Many runs hit the step limit because the simple stress rules could not drive the synthetic graphs to the loose acceptance threshold — yet focus never exploded.

This constitutes a first deliberate attempt to falsify the bounded-focus claim. It did not falsify it on these instances.

Full raw data: `results/epgrm_stress_sweep_*.csv`

## Classification of All Statements
- Established: only claims about what the specific simulator does on the runs performed.
- Supported Inference: the scaling behavior vs. the chosen baselines on these workloads.
- Working Hypothesis: generalization beyond current tasks + implementation.

No broader claims about "solving the von Neumann bottleneck" or "new computational paradigm working" are made at this stage.

## Instrumentation Added
See `src/metrics.py` + integration in `EPGRMSimulator`:
- rewrites_attempted / accepted / rejected
- verification_calls
- node_visits, edge_traversals
- focus_adds / evictions / size over time
- per-step timing + sampled memory
- graph size at each step
- checkpoint accounting

## Immediate Plan (following feedback)
- Continue exclusively on EP-GRM for now.
- Use stress dimensions (depth/width/density/cycles/conflicts/edits) instead of just numbered task types.
- Generate plots/tables from the CSV data (peak focus vs final graph nodes, verification work vs size, etc.).
- Add more adversarial generators (conflicting constraints, dense local neighborhoods, disconnected components).
- Improve rule quality or add scheduler to give the simulator a better chance of making progress on hard graphs (so we can measure full-run behavior).
- Add fault injection and checkpoint/restore experiments.
- Never add a second architecture (e.g. HB-AE) until EP-GRM has been thoroughly stressed and either survives or the failure modes are clearly documented.

## Artifacts
- Enhanced simulator with instrumentation: `src/epgrm_sim.py`, `src/metrics.py`
- Stress generators: `src/tasks/stress.py`
- Sweep runner: `experiments/stress_sweep.py`
- Updated linear runner
- Tests still passing

---

*Language in this document deliberately follows the precision requested. Broader conclusions will only be drawn after substantially more falsification attempts.*
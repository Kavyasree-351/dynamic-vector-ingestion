> Historical workspace instructions. Use README.md for this standalone repository.

# Direction A: dynamic vector ingestion and recall calibration

This package executes a rigorous **exploratory pilot**. Read `PROTOCOL.md` before `FINDINGS.md`. Do not assume the user's failure hypothesis, a new guarantee, prohibitive recalibration overhead or publication novelty has been established. Final queries remain unevaluated. Full confirmation/benchmarks and paper preparation are conditional and pending.

Start with `OVERVIEW.md` for the concise result and mathematical update; `FINDINGS.md` contains every method/state and limitations. The full numerical output is in CSV/JSON/NPZ, not just selected rows.

## Reproduction, Windows PowerShell

Run from the workspace directory containing `outputs` and `work`:

```powershell
python -m venv work/dynamic-venv
work/dynamic-venv/Scripts/python.exe -m pip install -r outputs/dynamic-ingestion/requirements.txt
work/dynamic-venv/Scripts/python.exe outputs/dynamic-ingestion/download.py
work/dynamic-venv/Scripts/python.exe outputs/dynamic-ingestion/experiment.py smoke
work/dynamic-venv/Scripts/python.exe outputs/dynamic-ingestion/experiment.py pilot --modes iid boundary retrain --seeds 0 1 2 3 4
work/dynamic-venv/Scripts/python.exe outputs/dynamic-ingestion/validate.py
work/dynamic-venv/Scripts/python.exe outputs/dynamic-ingestion/memory_profile.py
work/dynamic-venv/Scripts/python.exe outputs/dynamic-ingestion/report.py
```

Existing installation used here (Python 3.12.6):

```powershell
$env:PYTHONPATH = (Resolve-Path work/deps).Path
python outputs/dynamic-ingestion/download.py
python outputs/dynamic-ingestion/experiment.py smoke
python outputs/dynamic-ingestion/experiment.py pilot --modes iid boundary retrain --seeds 0 1 2 3 4
python outputs/dynamic-ingestion/validate.py
python outputs/dynamic-ingestion/memory_profile.py
python outputs/dynamic-ingestion/report.py
```

IID-only phase:

```powershell
python outputs/dynamic-ingestion/experiment.py pilot --modes iid --seeds 0 1 2 3 4
```

All pilot modes can be run in one command without selecting outcomes. Every seed receives a separate corpus selection, arrival order, index seed and exploratory query split. Query splits use ONLY the previously explored 2,000-query pool; remaining official queries remain reserved. The `inputs/` JSON files carry exact source hashes and the pool definition, so no earlier source-code package is required. Raw data are stored in `work/adaptive-retrieval`, shared with the previous project, not duplicated in ZIP. Pass `--data ABSOLUTE_PATH` to download/pilot if relocating. About 160 MB raw download storage plus scientific dependencies is required.

## Full-stage command and honest current limitation

```powershell
python outputs/dynamic-ingestion/experiment.py full
```

This command deliberately exits with an explanation and opens no reserved queries. A production-scale full benchmark is **not implemented or claimed complete**: it needs a passed failure gate, distinct contribution/closest-work clearance, fixed candidate settings and a frozen independent-confirmation protocol. The current driver cannot silently promote exploratory observations into final results. No human permission is being requested; this is the scientific stop rule the user required.

## Components

- `data.py`, `download.py`: hash-verified public inputs and exact exploratory/reserved separation.
- `index.py`: CPU IVF, insertion, optional rebuilding, workload construction, exact reference neighbors and incremental exact top-k merge.
- `calibration.py`: known CRC/Hoeffding and reusable exact-label caches.
- `experiment.py`: smoke tests, all methods, audit ablations and stream evaluation.
- `report.py`: all-condition CSV, mean/SD summaries, gate decision, Markdown write-up, LaTeX table fragment, PNG/PDF figures and manifest.
- `validate.py`: checks all 30 runs, paired outcomes, split separation, guard dominance and cached/full equality.
- `memory_profile.py`: isolated-process sampled RSS for full/cached/64-query calibration at the first +5% IID update on seed 0, one configuration per dataset/method. A diagnostic only; sampled peaks may miss brief allocations and include interpreter/data/index memory.
- `THEORY_AND_PRIOR_WORK.md`: mathematical rules/proofs, assumptions, established baselines and remaining novelty questions.

Nine budget methods plus the insertion guard are evaluated at six corpus states. The light 64-query update and 256-query ablation are standard small-sample recalibration candidates, not renamed inventions. The naive full-CRC baseline is complemented by exact cached full-CRC, so savings are not attributed solely to avoiding an unnecessarily expensive brute-force baseline. Feedback is post-state and has no claimed immediate guarantee. All methods are compared on the same queries, states, k, alpha and index for each scenario; the guard explicitly retains the initial index by design.

## Metrics and interpretation

`results.csv` contains per-run mean FNR, 2,000-resample conditional query-bootstrap intervals, paired drift intervals, distance counts, calibrated budget and calibration-kernel wall time. `summary.csv` contains across-seed means and sample SD. Query distance counts exclude the common 64 centroid comparisons; exact search can omit that overhead. Calibration centroid counts are a separate field. Query work is trace replay, not a measured serving latency benchmark.

The `drift` fields compare each method's current loss to the SAME query's **initial static-CRC loss**, not to that method's own initial loss. The static-CRC failure gate therefore measures exactly initial-to-current static-policy drift.

Calibration retained-byte metrics count exact top-k distances/IDs only. They exclude the query matrix and index. `cal_workspace_proxy_bytes` is a selected-array analytic proxy, **not measured or total peak memory**; it omits conversion and other temporary allocations. Raw JSON runs initially used the misleading field name `cal_estimated_peak_workspace_bytes`; report generation maps it to the accurate proxy name without changing values. This primary proxy is not an OS/RSS measurement. The separate memory_profile.json supplies limited sampled-RSS diagnostics; no serving-memory claim is made. Actual end-to-end latency and total peak memory remain required for a positive systems claim.

The label-array byte field is an output footprint, not minimal persistent deployment memory: only the cache methods retain label arrays between updates. The insertion guard requires no new calibration arrays after initialization; aggregation corrects that derived accounting to zero. Total calibration/query distance fields in CSV include centroid work; corpus-only fields remain available separately.

The rounded feedback controller showed instability on image vectors; see `feedback_instability.png` and the full findings. It is a heuristic, not a faithful implementation of published Rolling Risk Control. Its poor performance is not evidence of novelty for the audit method.

`tables.tex` is a verified exploratory table fragment, not a paper. `trajectories.png` and `.pdf` show mean Â± seed SD; seeds share a public query pool. All official final-query vectors remain unprocessed. A useful engineering implementation does not establish an original research contribution.

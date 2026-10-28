# Dynamic Vector Ingestion

A reproducible CPU vector-search study of recall calibration as an IVF corpus grows or its centroids are rebuilt. Includes static CRC, periodic recalibration, exact incremental calibration caches, small-query audits, conservative insertion guards and uncertainty/efficiency reporting.

**Outcome:** the tested ingestion settings did not establish the predefined replicated recall breakdown. Useful incremental engineering was verified; a new publishable algorithm was not established. This prototype is not a faithful ConANN/Quake/HNSW reproduction.

Read [OVERVIEW.md](OVERVIEW.md), [FINDINGS.md](FINDINGS.md), [PROTOCOL.md](PROTOCOL.md) and [THEORY_AND_PRIOR_WORK.md](THEORY_AND_PRIOR_WORK.md).

## Standalone quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_checks.py
.\.venv\Scripts\python.exe download.py
.\.venv\Scripts\python.exe experiment.py pilot --seeds 0 1 2 3 4
.\.venv\Scripts\python.exe validate.py
.\.venv\Scripts\python.exe report.py
```

Run from this repository root. Linux/macOS: use `.venv/bin/python`. Inputs download to the ignored, repository-local `work/datasets` folder; `--data PATH` overrides it. Bounded checks use synthetic inputs or existing result traces and require no dataset download. Python 3.12 and exact scientific-library pins were used. Full/final experiments are gated and have not been completed; do not weaken gates or relabel explored queries as fresh data.

## Included artifacts

Two datasets, five seeds and three mutation modes; all 1800 state/method conditions and raw paired traces are retained. `validate.py` checks the saved outcomes without opening new queries. Optional `memory_profile.py` measures sampled RSS, with explicit limitations. Distance-operation counts are not serving latency; sources and exact split IDs are in provenance files. Final queries remain unevaluated.

See [PUBLICATION.md](PUBLICATION.md) for publication scope/license status and [THIRD_PARTY.md](THIRD_PARTY.md) for attribution. `ORIGINAL_README.md` is archival; use the commands above for this standalone repository.

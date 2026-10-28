# Dynamic vector ingestion: verified exploratory findings

30 completed five-seed scenario runs; 1800 state/method conditions. Read PROTOCOL.md for the frozen gates and THEORY_AND_PRIOR_WORK.md for the guarantee distinctions. No full experiment, independent confirmation or novel-method paper is claimed.

## Failure gate

| Dataset / mutation | Complete | Failure gate passed |
|---|---|---|
| glove_iid | True | False |
| glove_boundary | True | False |
| glove_retrain | True | False |
| fashion_iid | True | False |
| fashion_boundary | True | False |
| fashion_retrain | True | False |

## Static initial calibration trajectory

FNR mean ± sample SD across five corpus/index/query-split seeds. Individual conditional query-bootstrap intervals and paired initial-to-current drift intervals are in results.csv. These exploratory seeds share an underlying query pool and are not five independent production datasets.

| Dataset | Mutation | Corpus fraction | Static CRC FNR | Static Hoeffding FNR |
|---|---|---:|---:|---:|
| fashion | boundary | 60% | 0.0568 ± 0.0292 | 0.0238 |
| fashion | boundary | 65% | 0.0562 ± 0.0303 | 0.0233 |
| fashion | boundary | 70% | 0.0569 ± 0.0309 | 0.0239 |
| fashion | boundary | 75% | 0.0566 ± 0.0314 | 0.0239 |
| fashion | boundary | 80% | 0.0581 ± 0.0309 | 0.0252 |
| fashion | boundary | 100% | 0.0603 ± 0.0324 | 0.0270 |
| fashion | iid | 60% | 0.0548 ± 0.0044 | 0.0275 |
| fashion | iid | 65% | 0.0529 ± 0.0046 | 0.0261 |
| fashion | iid | 70% | 0.0517 ± 0.0041 | 0.0258 |
| fashion | iid | 75% | 0.0507 ± 0.0045 | 0.0250 |
| fashion | iid | 80% | 0.0498 ± 0.0049 | 0.0245 |
| fashion | iid | 100% | 0.0471 ± 0.0038 | 0.0227 |
| fashion | retrain | 60% | 0.0548 ± 0.0044 | 0.0275 |
| fashion | retrain | 65% | 0.0523 ± 0.0052 | 0.0240 |
| fashion | retrain | 70% | 0.0494 ± 0.0025 | 0.0230 |
| fashion | retrain | 75% | 0.0476 ± 0.0020 | 0.0225 |
| fashion | retrain | 80% | 0.0510 ± 0.0066 | 0.0249 |
| fashion | retrain | 100% | 0.0431 ± 0.0039 | 0.0220 |
| glove | boundary | 60% | 0.0879 ± 0.0108 | 0.0403 |
| glove | boundary | 65% | 0.0874 ± 0.0095 | 0.0397 |
| glove | boundary | 70% | 0.0885 ± 0.0096 | 0.0409 |
| glove | boundary | 75% | 0.0895 ± 0.0101 | 0.0417 |
| glove | boundary | 80% | 0.0891 ± 0.0112 | 0.0416 |
| glove | boundary | 100% | 0.0917 ± 0.0079 | 0.0418 |
| glove | iid | 60% | 0.0925 ± 0.0104 | 0.0412 |
| glove | iid | 65% | 0.0915 ± 0.0110 | 0.0409 |
| glove | iid | 70% | 0.0898 ± 0.0111 | 0.0401 |
| glove | iid | 75% | 0.0872 ± 0.0107 | 0.0385 |
| glove | iid | 80% | 0.0863 ± 0.0099 | 0.0382 |
| glove | iid | 100% | 0.0830 ± 0.0110 | 0.0372 |
| glove | retrain | 60% | 0.0925 ± 0.0104 | 0.0412 |
| glove | retrain | 65% | 0.0922 ± 0.0082 | 0.0383 |
| glove | retrain | 70% | 0.0905 ± 0.0111 | 0.0385 |
| glove | retrain | 75% | 0.0849 ± 0.0046 | 0.0364 |
| glove | retrain | 80% | 0.0910 ± 0.0059 | 0.0386 |
| glove | retrain | 100% | 0.0796 ± 0.0095 | 0.0342 |

## Final cumulative state: method comparison

These are exploratory 100%-corpus states, NOT the untouched final query set. Different realized risks mean query work is not a matched-risk superiority comparison. Calibration work/time is summed over all six states before averaging across seeds.

| Dataset | Mutation | Method | FNR mean ± SD | Query corpus distances | Total calibration corpus distances | Total calibration seconds | Top-k label array bytes |
|---|---|---|---:|---:|---:|---:|---:|
| fashion | boundary | audit256_crc | 0.0606 ± 0.0329 | 541 | 2560000 | 1.416 | 40960 |
| fashion | boundary | audit64_crc | 0.0466 ± 0.0037 | 576 | 640000 | 0.377 | 10240 |
| fashion | boundary | cached_full_crc | 0.0466 ± 0.0037 | 576 | 10000000 | 5.366 | 160000 |
| fashion | boundary | exact | 0.0000 ± 0.0000 | 10000 | 0 | 0.000 | 0 |
| fashion | boundary | exact_delta_guard | 0.0263 ± 0.0158 | 4310 | 6000000 | 2.841 | 0 |
| fashion | boundary | feedback64 | 0.1861 ± 0.1489 | 724 | 640000 | 0.377 | 10240 |
| fashion | boundary | full_crc | 0.0466 ± 0.0037 | 576 | 45000000 | 20.611 | 160000 |
| fashion | boundary | periodic_crc | 0.0466 ± 0.0037 | 576 | 31000000 | 14.372 | 160000 |
| fashion | boundary | static_crc | 0.0603 ± 0.0324 | 538 | 6000000 | 2.841 | 0 |
| fashion | boundary | static_hoeffding | 0.0270 ± 0.0129 | 726 | 6000000 | 2.841 | 0 |
| fashion | iid | audit256_crc | 0.0471 ± 0.0038 | 539 | 2560000 | 1.319 | 40960 |
| fashion | iid | audit64_crc | 0.0471 ± 0.0038 | 539 | 640000 | 0.372 | 10240 |
| fashion | iid | cached_full_crc | 0.0471 ± 0.0038 | 539 | 10000000 | 5.120 | 160000 |
| fashion | iid | exact | 0.0000 ± 0.0000 | 10000 | 0 | 0.000 | 0 |
| fashion | iid | exact_delta_guard | 0.0271 ± 0.0025 | 4323 | 6000000 | 2.869 | 0 |
| fashion | iid | feedback64 | 0.2437 ± 0.1366 | 561 | 640000 | 0.372 | 10240 |
| fashion | iid | full_crc | 0.0471 ± 0.0038 | 539 | 45000000 | 20.584 | 160000 |
| fashion | iid | periodic_crc | 0.0471 ± 0.0038 | 539 | 31000000 | 13.887 | 160000 |
| fashion | iid | static_crc | 0.0471 ± 0.0038 | 539 | 6000000 | 2.869 | 0 |
| fashion | iid | static_hoeffding | 0.0227 ± 0.0031 | 712 | 6000000 | 2.869 | 0 |
| fashion | retrain | audit256_crc | 0.0431 ± 0.0039 | 545 | 2560000 | 1.447 | 40960 |
| fashion | retrain | audit64_crc | 0.0431 ± 0.0039 | 545 | 640000 | 0.424 | 10240 |
| fashion | retrain | cached_full_crc | 0.0431 ± 0.0039 | 545 | 10000000 | 5.385 | 160000 |
| fashion | retrain | exact | 0.0000 ± 0.0000 | 10000 | 0 | 0.000 | 0 |
| fashion | retrain | exact_delta_guard | 0.0271 ± 0.0025 | 4323 | 6000000 | 3.144 | 0 |
| fashion | retrain | feedback64 | 0.1927 ± 0.1537 | 545 | 640000 | 0.424 | 10240 |
| fashion | retrain | full_crc | 0.0431 ± 0.0039 | 545 | 45000000 | 23.339 | 160000 |
| fashion | retrain | periodic_crc | 0.0431 ± 0.0039 | 545 | 31000000 | 16.454 | 160000 |
| fashion | retrain | static_crc | 0.0431 ± 0.0039 | 545 | 6000000 | 3.144 | 0 |
| fashion | retrain | static_hoeffding | 0.0220 ± 0.0024 | 723 | 6000000 | 3.144 | 0 |
| glove | boundary | audit256_crc | 0.0784 ± 0.0078 | 2428 | 5120000 | 0.434 | 40960 |
| glove | boundary | audit64_crc | 0.0843 ± 0.0221 | 2357 | 1280000 | 0.119 | 10240 |
| glove | boundary | cached_full_crc | 0.0917 ± 0.0079 | 2158 | 20000000 | 1.664 | 160000 |
| glove | boundary | exact | 0.0000 ± 0.0000 | 20000 | 0 | 0.000 | 0 |
| glove | boundary | exact_delta_guard | 0.0421 ± 0.0048 | 9226 | 12000000 | 0.847 | 0 |
| glove | boundary | feedback64 | 0.0907 ± 0.0233 | 2225 | 1280000 | 0.119 | 10240 |
| glove | boundary | full_crc | 0.0917 ± 0.0079 | 2158 | 90000000 | 6.239 | 160000 |
| glove | boundary | periodic_crc | 0.0917 ± 0.0079 | 2158 | 62000000 | 4.356 | 160000 |
| glove | boundary | static_crc | 0.0917 ± 0.0079 | 2158 | 12000000 | 0.847 | 0 |
| glove | boundary | static_hoeffding | 0.0418 ± 0.0066 | 3650 | 12000000 | 0.847 | 0 |
| glove | iid | audit256_crc | 0.0886 ± 0.0080 | 2254 | 5120000 | 0.436 | 40960 |
| glove | iid | audit64_crc | 0.0976 ± 0.0264 | 2191 | 1280000 | 0.123 | 10240 |
| glove | iid | cached_full_crc | 0.0886 ± 0.0080 | 2254 | 20000000 | 1.752 | 160000 |
| glove | iid | exact | 0.0000 ± 0.0000 | 20000 | 0 | 0.000 | 0 |
| glove | iid | exact_delta_guard | 0.0469 ± 0.0065 | 9427 | 12000000 | 0.850 | 0 |
| glove | iid | feedback64 | 0.1048 ± 0.0268 | 2065 | 1280000 | 0.123 | 10240 |
| glove | iid | full_crc | 0.0886 ± 0.0080 | 2254 | 90000000 | 6.213 | 160000 |
| glove | iid | periodic_crc | 0.0886 ± 0.0080 | 2254 | 62000000 | 4.260 | 160000 |
| glove | iid | static_crc | 0.0830 ± 0.0110 | 2380 | 12000000 | 0.850 | 0 |
| glove | iid | static_hoeffding | 0.0372 ± 0.0055 | 3998 | 12000000 | 0.850 | 0 |
| glove | retrain | audit256_crc | 0.0868 ± 0.0103 | 2278 | 5120000 | 0.417 | 40960 |
| glove | retrain | audit64_crc | 0.0868 ± 0.0235 | 2341 | 1280000 | 0.116 | 10240 |
| glove | retrain | cached_full_crc | 0.0932 ± 0.0097 | 2150 | 20000000 | 1.737 | 160000 |
| glove | retrain | exact | 0.0000 ± 0.0000 | 20000 | 0 | 0.000 | 0 |
| glove | retrain | exact_delta_guard | 0.0469 ± 0.0065 | 9427 | 12000000 | 0.753 | 0 |
| glove | retrain | feedback64 | 0.0962 ± 0.0342 | 2214 | 1280000 | 0.116 | 10240 |
| glove | retrain | full_crc | 0.0932 ± 0.0097 | 2150 | 90000000 | 6.314 | 160000 |
| glove | retrain | periodic_crc | 0.0932 ± 0.0097 | 2150 | 62000000 | 4.293 | 160000 |
| glove | retrain | static_crc | 0.0796 ± 0.0095 | 2406 | 12000000 | 0.753 | 0 |
| glove | retrain | static_hoeffding | 0.0342 ± 0.0040 | 4048 | 12000000 | 0.753 | 0 |

## Diagnostic memory samples

Separate processes, seed 0, IID 60% to 65% corpus update. RSS sampled every 5ms; includes interpreter, data and index. Increments are relative to each process immediately before the kernel. These can miss brief peaks and are not exact peak-memory or serving measurements. A zero sampled increase can reflect allocator reuse or sampling resolution; it does not mean zero allocations.

| Dataset | Method | RSS before (MiB) | Sampled peak RSS (MiB) | Sampled increase (MiB) |
|---|---|---:|---:|---:|
| glove | full_crc | 170.92 | 186.18 | 15.27 |
| glove | cached_full_crc | 172.46 | 172.50 | 0.04 |
| glove | audit64_crc | 170.76 | 171.29 | 0.53 |
| fashion | full_crc | 204.48 | 289.96 | 85.48 |
| fashion | cached_full_crc | 205.67 | 217.67 | 12.00 |
| fashion | audit64_crc | 205.30 | 211.38 | 6.07 |

## Scientific interpretation

The primary IID hypothesis passes only if replicated_failure_by_mode.iid is true. Boundary-late arrival is an engineered diagnostic and retraining changes geometry: even if either fails, it must not be reported as a failure of ordinary IID fixed-centroid ingestion. All counts and modes are retained in gate.json. No pilot-driven stress search or fresh-query validation has been done.

Cached full CRC must match full current-corpus calibration exactly; the harness asserts equal exact IDs, losses and selected budgets. Thus repeated full brute-force relabeling is not the strongest baseline. The 64/256/all-query ablations test a known calibration sample-size tradeoff, not a new update theorem. Exact-delta guarding has a deterministic insertion-only dominance argument but adds query work; it is a strong conservative control, not evidence that all conservative solutions require full search.

The prespecified rounded, high-gain feedback controller oscillated badly on image vectors. This is a negative finding about that heuristic, NOT a refutation of published Rolling Risk Control. Its separate feedback_instability figure and all raw outcomes are retained; it must not be used as a weakened stand-in for a faithful strong online baseline.

## Limits and pending evidence

- Small CPU IVF prototype; no faithful ConANN score, Quake, DARTH+ or graph-index reproduction. Coarse integer probe budgets can leave substantial initial risk slack, masking a failure that a tighter score-based policy might show. No claim that these systems fail or that all dynamic-index calibration is safe.
- Corpus/query split seeds vary, but public queries have been explored in earlier work; no independent confirmation. Reserved queries remain unevaluated.
- Engineered arrival order is not chronological production ingestion. Raw Fashion pixels are a second geometry, not modern dense retrieval embeddings.
- Corpus-only ingestion/retraining, no deletions, mixed updates or query drift. An insertion-only guard does not establish deletion safety.
- Calibration kernel times include exact labels/cache update and loss curves, excluding index build, data load, bootstrap, and final scalar budget selection. Vector-distance counts separately include calibration centroids in results.csv. Index build/mutation times are recorded separately.
- Query work is replayed distance count, not observed serving latency. Add 64 centroid distances for IVF/guard; full exact search need not compute centroids.
- The legacy cal_retained_bytes metric counts top-k label arrays produced by a kernel, not minimal persistent deployment memory. Only cache methods need to retain those arrays between updates. It excludes the raw audit-query matrix, corpus and index. The guard needs no new label arrays after initialization; aggregation corrects that derived accounting to zero. The legacy field cal_estimated_peak_workspace_bytes is normalized to cal_workspace_proxy_bytes: a selected-array proxy, NOT total/measured peak memory. Dtype conversion, allocator/BLAS and other temporaries add memory.
- CRC expectation, Hoeffding population-risk confidence, cumulative feedback control and per-query safety are different guarantees. No anytime or distribution-free drift guarantee for the rounded feedback controller is claimed.
- A discovery paper requires a real replicated failure, distinct contribution beyond standard cache/subsample/feedback repairs, matched-risk efficiency, fresh confirmation, another index family, serving latency/memory measurement and completed closest-work review. All remain pending unless separately documented.

## Attempt ledger

1. Frozen protocol, three mutation modes and failure thresholds before inspecting outcomes.
2. Smoke-tested exact candidate recall, cache identity under insertions/ties and guard dominance.
3. First unoptimized IID seed showed decreasing error. Replaced full sorting with an exact boundary-tie-aware top-k partition kernel and removed repeated float64 conversions; verified against stable full sorting. Interrupted preliminary sweep and regenerated ALL results with the same faster kernel for fair timing. No seed or mode was selected based on favorable outcomes.
4. All calibration/evaluation truth is CURRENT-corpus truth. Cached update equality checked at every state.
5. No paper draft or reserved-query evaluation. See gate.json for the mechanical stop decision.
6. Added a synthetic boundary-crossing positive control after observing the exploratory negative trend: static FNR changes from 0 to 1, and recalibration selects exact search. This tests harness sensitivity, not a realistic replicated failure or novelty.
7. Reused identical paired bootstrap resamples as count matrices and switched public CORPUS loading to contiguous reads to avoid h5py overhead. Completed runs were resumed without outcome filtering. Neither change alters queried vectors, distances, budgets, calibration kernels or scientific outcomes. The workspace estimate field was renamed as a proxy for accuracy; no measured values were changed.

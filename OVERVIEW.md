# Direction A — concise outcome

**Status: exploratory prototype; novelty not established.** No reserved final queries have been evaluated.

## Test and decision

Two public vector geometries, five independent corpus/index/query-split seeds, IID insertion plus two prespecified diagnostics (boundary-heavy arrivals and centroid retraining). Start at 60% corpus; evaluate 65%, 70%, 75%, 80% and 100%. k=10, alpha=.10, 64 IVF lists. A replicated failure requires FNR>.12, bootstrap lower bound>.10 and >.02 paired increase at two adjacent states in >=4/5 seeds on BOTH datasets.

| Mutation | Replicated failure gate |
|---|---|
| iid | False |
| boundary | False |
| retrain | False |

## Primary IID static-CRC result

| Dataset | Initial mean FNR ± seed SD | 100%-corpus mean FNR ± seed SD |
|---|---:|---:|
| glove | 0.0925 ± 0.0104 | 0.0830 ± 0.0110 |
| fashion | 0.0548 ± 0.0044 | 0.0471 ± 0.0038 |

## Tested update and strongest control

Maintain exact calibration top-k by T_t(q)=TopK(T_(t-1)(q) union new_batch). Update current IVF losses, then choose the smallest p satisfying (1+sum_i loss_t(q_i,p))/(m+1)<=alpha. m=64 is the lightweight candidate; m=256 and m=1000 are ablations/controls. Full cached m=1000 produces exactly the same budgets and FNR as full brute-force recalibration. This is a standard incremental computation plus standard CRC, not a new algorithm.

| Dataset (IID) | Method | Final FNR | Final query distances | Calibration vector distances, summed over stream |
|---|---|---:|---:|---:|
| glove | static_crc | 0.0830 | 2380 | 12000000 |
| glove | full_crc | 0.0886 | 2254 | 90000000 |
| glove | cached_full_crc | 0.0886 | 2254 | 20000000 |
| glove | audit64_crc | 0.0976 | 2191 | 1280000 |
| glove | exact_delta_guard | 0.0469 | 9427 | 12000000 |
| fashion | static_crc | 0.0471 | 539 | 6000000 |
| fashion | full_crc | 0.0471 | 539 | 45000000 |
| fashion | cached_full_crc | 0.0471 | 539 | 10000000 |
| fashion | audit64_crc | 0.0471 | 539 | 640000 |
| fashion | exact_delta_guard | 0.0271 | 4323 | 6000000 |

## Meaning and limits

A changing corpus invalidates automatic transfer of a static certificate, but does not imply upward risk drift. With fixed Voronoi cells and locally supported IID arrivals, new neighbors can become more concentrated inside the query cell; an elementary binomial bound explaining this is in THEORY_AND_PRIOR_WORK.md. It is not claimed as a novel theorem.

If all failure gates are false, the required Phase-1 mechanism was not established and full experiments should stop. The code supplies a useful exact calibration-maintenance solution, but cannot turn this engineering reuse into a top-tier contribution. Quake already addresses dynamic vector indexing; generic online risk adaptation is also established.

All results are exploratory and small-scale. Cached/partial methods have pointwise mean-risk guarantees under their stated independence assumptions, not per-query or anytime guarantees. No faithful ConANN/Quake/DARTH+ reproduction, independent confirmation, HNSW/deletion study, total peak-memory or serving-latency benchmark is complete. Read FINDINGS.md for every state/method, uncertainty, calibration times, memory limits and attempted alternatives. Full-stage and paper results remain pending.

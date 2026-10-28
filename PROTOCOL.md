# Dynamic-ingestion feasibility protocol — frozen 27 October 2026

## Scientific status
The user's dynamic-index mechanism is a HYPOTHESIS, not an established literature gap. Fixed-centroid IVF insertion changes populations/nearest-neighbor identities, not Voronoi boundaries. Rebuilding centroids does change boundaries. A corpus changing does not by itself imply recall must deteriorate. No guarantee of novelty or a paper.

ConANN already supplies static conformal ANN control. Quake (OSDI 2025) studies changing corpora, index maintenance and adaptive recall. Rolling Risk Control (TMLR 2023) already supplies online bounded-loss adaptation; a simple feedback controller is not new. DARTH+ is still an unresolved full-text comparison. No faithful reproduction of these systems is claimed by a NumPy budget-based IVF prototype.

## Data and independence
Reuse public GloVe-25 and official Fashion-MNIST inputs, verified by saved hashes from the prior project. Corpus sizes 20,000 and 10,000. Independent corpus selection/order and query split seeds 0..4. Only the SAME 2,000 already explored query IDs from the previous project may be used for this study's design/calibration/pilot; the remaining 8,000 query IDs are reserved and must not be indexed/read as query arrays/evaluated. Repartition the 2,000 pool into 400 design, 1,000 calibration, 600 pilot per seed. Prior pilot data are exploratory, NOT independent confirmation. Fashion gzip bytes must be decompressed; reserved image vectors are never transformed, fitted or evaluated. No query-derived index or arrival construction.

Initial corpus=60% of selected pool; cumulative states=60,65,70,75,80,100%. These are percentage points of the final selected corpus, not growth percentages relative to the initial corpus. k=10, 64 lists, alpha=.10. Five independent corpus/index/split seeds. Query distribution stays fixed during Direction A. Exact neighbors are recomputed against each CURRENT corpus; never evaluate with stale ground truth. Float64 reference distances with deterministic distance/ID tie ordering. Numeric operations single-threaded.

## Primary and prespecified diagnostics
1. IID arrival: random corpus order, centroids trained on initial slice only and frozen.
2. Boundary-late arrival: a query-independent auxiliary clustering on corpus vectors ranks vectors by closest/second-closest centroid distance ratio; low ambiguity first, high ambiguity late. This is an engineered covariate-skew diagnostic, NOT a real chronological stream. All corpus features may define workload generation; no query/recall labels. Evaluate all states/seeds, no search over stress strengths.
3. Retraining: IID arrival, 64 centroids refit on each cumulative corpus, static initial budget retained. Distinguish index retraining from insertion-only.

These diagnostics are declared before performance and retained regardless of sign. No continually increasing stress until a convenient failure is obtained. If none passes, investigate Direction B in a separately declared exploratory diagnostic, without consuming reserved queries; do not assert that drift or OOD automatically implies novelty.

## Methods and costs
- Static initial CRC: smallest p with (sum(cal FNR)+1)/(1001)<=alpha; full-search fallback.
- Static initial Hoeffding: uniform bound over 64 budgets, delta=.05; different high-probability guarantee, exact fallback.
- Every-state full CRC, brute-force CURRENT corpus labels (reference recalibration); do not assume it fails or is prohibitively costly.
- Periodic CRC every two post-initial states, plus final state; stale between refreshes.
- Cached full CRC: exact initial calibration top-k, merge only new-batch distances into cached top-k, recompute current cluster ranks; choose same CRC budget as every-state full recalibration. This is a strong KNOWN incremental computation baseline, not a novel algorithm.
- Lightweight candidate: same exact cached update for a fixed random 64-query audit subset, CRC correction with n=64, no tuning. Ablation: 256 audits and all 1,000. Index/corpus construction independent of these queries. Pointwise expected-risk guarantee under IID queries; no per-query, realized-sample or anytime guarantee. Default 64 is fixed before evaluation.
- Feedback baseline: integer probe controller updated AFTER each state using current 64-audit loss at current budget; next budget=clip(p+ceil(64*(mean loss-alpha)),1,64). This is a heuristic instantiation of known feedback adaptation, not a martingale theorem; current-state risk need not be controlled.
- Exact-delta guard: freeze initial IVF search for old corpus; scan ALL added vectors exactly and merge. In insertion-only states its missing-true-neighbor count cannot increase relative to initial approximate top-k, pointwise. This elementary top-k inclusion lemma is not claimed as new. Invalid under deletions or query shift; independent of mutated-index geometry because it searches the frozen old index. Report query overhead proportional to cumulative delta rather than claiming every conservative method must scan all vectors.
- Full exact search, zero FNR.

Ground-truth evaluation work is separate from method-charged calibration. Count calibration query-vector distances AND centroid distances, retained arrays and observed wall time. Measure actual full/cached/audit calibration kernels, not infer time savings from arithmetic alone. Peak temporary memory is an analytic operator-workspace estimate, not an OS/RSS measurement. Pilot retrieval efficiency uses replayed exact distance-operation counts, not serving latency. Building/retraining assignment cost/time recorded separately and common to methods using the same index.

## Gates
Smoke before pilot: direct ANN candidate recall vs cluster-rank calculation; cached vs full top-k including ties; insertion-guard dominance; full-search zero loss; frozen-centroid invariance; loss monotonicity; query split disjointness.

Practical failure: at a common pair of adjacent post-initial states, static CRC has mean pilot FNR>.12, query-bootstrap lower 95% bound>.10, AND paired mean drift from initial>.02, in >=4/5 seeds. Report gate per dataset/mutation; only call a replicated mechanism if it holds on BOTH independently sourced datasets. Initial state should meet the target in expectation; report its observed uncertainty rather than promise each split meets .10. Secondary effects cannot replace the IID primary hypothesis without explicit labeling.

Candidate merit: only after failure gate, fixed audit candidate should maintain mean FNR<=.10 (allow sampling uncertainty explicitly), save >=50% calibration distance work against CACHED FULL baseline, and add <=10% query-distance work relative to that baseline across >=4/5 seeds, then pass fresh confirmation with frozen parameters and another index family. Generic audit CRC alone never establishes algorithmic novelty. Full runs require BOTH a credible distinct contribution/prior-work clearance and an opportunity gate; code must block `full` otherwise. No paper draft without this evidence.

Uncertainty: 2,000 paired query bootstrap resamples, conditional per fitted run; across-seed mean and sample standard deviation. Shared underlying query pool implies seeds are not independent external replications. No selective seed dropping. All modes, states, methods and audit ablations reported.

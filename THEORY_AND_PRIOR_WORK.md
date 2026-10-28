# What is and is not established

## Correct scope of the hypothesis

For corpus D_t and independently constructed IVF I_t, define

    L_t(q,p) = 1 - |ANN_k(q; I_t,p) intersection Exact_k(q;D_t)|/k.

Even if queries Q_i stay IID, the loss function changes when D_t or I_t changes. Thus an initial calibration certificate is not automatically a certificate for the current loss. However, this logical absence of a guarantee does NOT imply that risk increases. Fixed-centroid insertion changes list counts and ground truth; moving boundaries requires centroid retraining or partition maintenance. Queries themselves need not stop being exchangeable merely because a corpus changes.

## Why IID insertion can make fixed-centroid retrieval easier

This is an elementary geometric diagnostic, NOT a new theorem claim. Fix a query q strictly inside its nearest-centroid Voronoi cell. Let r>0 be any radius with B(q,r) wholly inside that cell. Suppose m NEW vectors arrive independently from a distribution having mass pi(q)>0 in that ball, with index geometry and q fixed independently of those new vectors. If at least k new vectors fall in the ball, the current true top-k (including any old vectors) all lie inside the same cell. Searching that cell exactly then has zero FNR. Consequently,

    E[L_m(q,p)] <= Pr[Binomial(m,pi(q)) < k], for every p>=1.

The right side tends to zero as m increases. Conditioning on the initial trained index is allowed because only the new arrivals are used in this argument. This does NOT prove finite-sample risk is monotone, does not apply to retrained boundaries, and can be uninformative for boundary/OOD queries with zero local mass. It explains why missing stationarity need not produce upward recall drift, and why an IID-ingestion failure must be demonstrated rather than presumed. The observation is basic nearest-neighbor geometry, not a claim of publishable originality.

## Static and updated CRC

For independent calibration queries Q_1..Q_n, current labels and a nested probe family p=1..P:

    p_t = min { p : [1 + sum_i L_t(Q_i,p)] / (n+1) <= alpha },

with deterministic exact search if no candidate qualifies. This is an application of existing CRC. The risk bound averages over calibration and fresh-query randomness at a FIXED corpus/index state. It is not a guarantee for every query, every realized calibration set, every adaptive query distribution or all stream times simultaneously.

Reusing the same calibration query pool at different times is not automatically invalid: when the corpus/index construction is independent of their outcomes, each state has its own pointwise CRC argument after its losses are correctly updated. If those outcomes influence ingestion, index training or policy-family selection, this argument needs further analysis. The implementation never uses calibration outcomes to build index geometry or order arrivals.

Hoeffding alternative: bound all P fixed-budget mean risks by

    R_t(p) <= mean_i L_t(Q_i,p) + sqrt(log(P/delta)/(2n)).

For an all-times finite-state confidence statement, a correction over the declared time horizon is additionally needed. The pilot reports pointwise guarantees, not an anytime claim.

## Exact cached update: a strong existing-computation control

Let T_{t-1}(q) be the exact top-k of the old corpus and B_t the newly inserted batch. Then

    T_t(q) = TopK(T_{t-1}(q) union B_t).

Thus exact calibration labels can be maintained using n*|B_t| new query-vector distances, not n*|D_t|. With fixed centroid identities, current losses follow from the cluster ranks of these k exact IDs; after retraining, reassign IDs and recompute query-centroid ranks. The pilot directly compares this update to full recomputation for EVERY calibration query/state. This elementary incremental top-k computation is NOT claimed as novel. It is essential to avoid exaggerating recalibration costs by comparing only to repeated brute force.

This sufficiency uses exact-within-list IVF and FIXED probe-budget policies. Global top-k IDs alone do not reconstruct arbitrary per-query stopping scores, quantized search, or HNSW traversal. In particular this is not a faithful incremental ConANN score update. A faithful score-based method could behave differently under ingestion, and the negative fixed-budget pilot cannot dismiss that possibility.

Lightweight candidate: keep an independently chosen m=64 audit-query cache, update those exact losses, apply the same CRC rule with n=m. Ablations m=256 and m=1000 measure the overhead/conservatism tradeoff. This is a known subsampled-calibration strategy; success would establish feasibility, not an original learning algorithm.

The measured persistent top-k arrays use 16*m*k bytes (float64 distances plus int64 IDs). Audit-query storage, index storage and kernel temporary allocations are additional; the harness does not claim a total peak-memory measurement.

## Insertion-only deterministic guard

Freeze the initial corpus D_0 and its approximate result A_0(q)=TopK(S_0(q)), where S_0 is the initial searched candidate subset. After insertion delta_t, return

    A_t(q) = TopK(A_0(q) union delta_t),

scanning all delta_t exactly. Every missed true neighbor at time t must be an old-corpus point missing from A_0. Every old point among current top-k was among initial top-k. Hence

    |T_t(q) minus A_t(q)| <= |T_0(q) minus A_0(q)|,
    L_t(q) <= L_0(q), for EVERY q.

Tie-breaking must use one consistent distance/ID order. This transfers an initial marginal guarantee without new feedback, at query work cost initial searched vectors + |delta_t|. It is invalid under deletions, changed old vectors or a shifted query population. This short set-inclusion lemma is a diagnostic/guard baseline, not advertised as an A*-level theorem or new architecture. The smoke test checks the actual candidate merging interpretation against this bound.

## Feedback control is a different guarantee

The supplied integer controller uses

    p_{t+1}=clip(p_t + ceil(64*(audit_mean_loss_t-alpha)),1,P).

The audit comes AFTER current-state predictions. This is a heuristic feedback baseline motivated by established online risk adaptation; no formal theorem for this clipped, rounded batch implementation is claimed. Long-run average control, immediate post-update mean-risk control, monitoring a violation, and per-query recall are different objectives. A martingale detector does not by itself repair retrieval or supply missing exact labels.

## Primary-source screening, accessed 27 October 2026

- [ConANN, PVLDB 19(1), 2025](https://www.vldb.org/pvldb/vol19/p29-horchidan.pdf), [official code](https://github.com/soniahorchidan/conann). Existing conformal mean-FNR control with a query-adaptive IVF stopping score. The current prototype uses simpler fixed probe budgets and cannot be called a faithful ConANN reproduction or a counterexample to its theorem. The published setup is static; a dynamic-index theorem gap still requires a complete extension review.
- [Quake, OSDI 2025](https://www.usenix.org/conference/osdi25/presentation/mohoney), [paper](https://www.usenix.org/system/files/osdi25-mohoney.pdf), [official implementation](https://github.com/marius-team/quake). Explicitly studies changing corpora, partition maintenance and adaptive recall targets. Dynamic vector search is NOT an unexplored application. Its recall estimator and statistical assumptions must be reproduced/compared before claiming a new capability. The paper is available; no implementation comparison has been run here.
- [Achieving Risk Control in Online Learning Settings](https://arxiv.org/abs/2205.09095), Feldman et al., TMLR 2023. Established Rolling Risk Control. Generic online feedback or changing thresholds is not new; its long-run guarantee must not be replaced by an immediate per-state guarantee. The OpenReview PDF endpoint requested during this run returned a browser-verification page; the indexed primary-paper excerpt and arXiv abstract are screening evidence, not a completed theorem reproduction.
- [Conformal Risk Control, ICLR 2024](https://research.google/pubs/conformal-risk-control/). Established bounded monotone-loss mean-risk calibration used here.
- [DARTH/DARTH+ author overview](https://mchatzakis.github.io/declarative-recall/). Existing recall prediction and optional probabilistic quality guarantees. Complete DARTH+ full-text assessment is STILL PENDING; prior access denial is not evidence of absent prior work.
- [ANN-Benchmarks official dataset inventory](https://github.com/erikbern/ann-benchmarks), [GloVe public mirror](https://huggingface.co/datasets/hhy3/ann-datasets). Corpus subsampled, current-corpus exact truth recomputed.
- [Fashion-MNIST official repository](https://github.com/zalandoresearch/fashion-mnist). Raw pixel vectors give a second geometric dataset, not independent evidence on production neural embeddings.

## Novelty decision

No contribution has yet been established. A realistic replicated static-calibration failure would clear ONLY the failure gate. A paper still needs a distinct capability or result that survives cached exact recalibration, the insertion guard, Quake and relevant online calibration baselines. Merely applying CRC after a cache update, using fewer audit queries, or renaming a feedback rule is insufficient.

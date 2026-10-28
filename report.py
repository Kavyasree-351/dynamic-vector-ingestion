"""Aggregate ALL runs with seed SD, paired query intervals and stop rules."""
import os,csv,json
from collections import defaultdict
import numpy as np
from data import ROOT,save,digest
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work'/'mpl-cache'))
def main():
    rows=[];runs=[]
    for path in sorted((ROOT/'results').glob('*_metrics.json')):
        obj=json.loads(path.read_text());rows+=obj['rows'];runs.append(obj)
    for row in rows:
        if 'cal_estimated_peak_workspace_bytes' in row:
            row['cal_workspace_proxy_bytes']=row.pop('cal_estimated_peak_workspace_bytes')
        row['cal_total_distances']=row['cal_vector_distances']+row['cal_centroid_distances']
        row['query_total_distances']=row['distances']+(0 if row['method']=='exact' else 64)
        if row['method']=='exact_delta_guard' and row['step']>0:row['cal_retained_bytes']=0
    assert rows,'No completed runs'
    with open(ROOT/'results.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    groups=defaultdict(list)
    for row in rows:groups[(row['dataset'],row['mode'],row['step'],row['method'])].append(row)
    summary=[]
    for key,rr in sorted(groups.items()):
        line=dict(zip(['dataset','mode','step','method'],key));line['seeds']=len(rr);line['fraction']=rr[0]['fraction']
        for field in ['fnr','distances','query_total_distances','cal_seconds','cal_vector_distances','cal_total_distances','cal_retained_bytes','cal_workspace_proxy_bytes']:
            vals=[r[field] for r in rr];line[field+'_mean']=float(np.mean(vals));line[field+'_sd']=float(np.std(vals,ddof=1)) if len(vals)>1 else None
        summary.append(line)
    with open(ROOT/'summary.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    gate={}
    for dataset in ['glove','fashion']:
        for mode in ['iid','boundary','retrain']:
            rr=[r for r in rows if r['dataset']==dataset and r['mode']==mode and r['method']=='static_crc']
            pairs={}
            for step in range(1,5):
                ok=[]
                for seed in range(5):
                    pair=[r for r in rr if r['seed']==seed and r['step'] in [step,step+1]]
                    if len(pair)==2 and all(r['fnr']>.12 and r['ci_low']>.1 and r['drift']>.02 for r in pair):ok.append(seed)
                pairs[str(step)+'-'+str(step+1)]=ok
            complete=len(rr)==30
            gate[dataset+'_'+mode]=dict(complete=complete,qualifying_seeds_by_adjacent_pair=pairs,passed=complete and any(len(v)>=4 for v in pairs.values()))
    replicated={m:all(gate[d+'_'+m]['passed'] for d in ['glove','fashion']) for m in ['iid','boundary','retrain']}
    save(ROOT/'gate.json',dict(failure_gate=gate,replicated_failure_by_mode=replicated,novelty_established=False,
                             full_experiments_authorized_by_scientific_gate=False,reserved_queries_evaluated=False))
    lines=['# Dynamic vector ingestion: verified exploratory findings','',
           f'{len(runs)} completed five-seed scenario runs; {len(rows)} state/method conditions. Read PROTOCOL.md for the frozen gates and THEORY_AND_PRIOR_WORK.md for the guarantee distinctions. No full experiment, independent confirmation or novel-method paper is claimed.','',
           '## Failure gate','',
           '| Dataset / mutation | Complete | Failure gate passed |','|---|---|---|']
    for key,v in gate.items():lines.append(f'| {key} | {v["complete"]} | {v["passed"]} |')
    lines+=['','## Static initial calibration trajectory','',
            'FNR mean ± sample SD across five corpus/index/query-split seeds. Individual conditional query-bootstrap intervals and paired initial-to-current drift intervals are in results.csv. These exploratory seeds share an underlying query pool and are not five independent production datasets.','',
            '| Dataset | Mutation | Corpus fraction | Static CRC FNR | Static Hoeffding FNR |','|---|---|---:|---:|---:|']
    for s in summary:
        if s['method']!='static_crc':continue
        h=next(x for x in summary if x['dataset']==s['dataset'] and x['mode']==s['mode'] and x['step']==s['step'] and x['method']=='static_hoeffding')
        sd=s['fnr_sd'] or 0
        lines.append(f'| {s["dataset"]} | {s["mode"]} | {s["fraction"]:.0%} | {s["fnr_mean"]:.4f} ± {sd:.4f} | {h["fnr_mean"]:.4f} |')
    lines+=['','## Final cumulative state: method comparison','',
            'These are exploratory 100%-corpus states, NOT the untouched final query set. Different realized risks mean query work is not a matched-risk superiority comparison. Calibration work/time is summed over all six states before averaging across seeds.','',
            '| Dataset | Mutation | Method | FNR mean ± SD | Query corpus distances | Total calibration corpus distances | Total calibration seconds | Top-k label array bytes |',
            '|---|---|---|---:|---:|---:|---:|---:|']
    latex=['% Exploratory current-corpus results; not a novel-method paper claim.','\\begin{tabular}{lllrrr}','\\hline','Dataset & Mutation & Method & FNR & Query work & Cal. seconds \\\\','\\hline']
    for s in summary:
        if s['step']!=5:continue
        rr=[r for r in rows if r['dataset']==s['dataset'] and r['mode']==s['mode'] and r['method']==s['method']]
        times=[sum(r['cal_seconds'] for r in rr if r['seed']==seed) for seed in range(5)]
        counts=[sum(r['cal_vector_distances'] for r in rr if r['seed']==seed) for seed in range(5)]
        lines.append(f'| {s["dataset"]} | {s["mode"]} | {s["method"]} | {s["fnr_mean"]:.4f} ± {(s["fnr_sd"] or 0):.4f} | {s["distances_mean"]:.0f} | {np.mean(counts):.0f} | {np.mean(times):.3f} | {s["cal_retained_bytes_mean"]:.0f} |')
        method=s['method'].replace('_',r'\_')
        latex.append(f'{s["dataset"]} & {s["mode"]} & {method} & {s["fnr_mean"]:.4f} & {s["distances_mean"]:.0f} & {np.mean(times):.3f} \\\\')
    latex+=['\\hline','\\end{tabular}'];(ROOT/'tables.tex').write_text('\n'.join(latex)+'\n')
    short_names={'static_crc':'Static CRC','static_hoeffding':'Static Hoeffding','full_crc':'Full CRC',
        'periodic_crc':'Periodic CRC','cached_full_crc':'Cached CRC (1000)','audit64_crc':'Audit CRC (64)',
        'audit256_crc':'Audit CRC (256)','feedback64':'Feedback (64)','exact':'Exact','exact_delta_guard':'Exact-delta guard'}
    for dataset in ['glove','fashion']:
        for mode in ['iid','boundary','retrain']:
            snippet=[f'% {dataset}, {mode}, 100%-corpus exploratory state. FNR mean +/- seed SD.',
                '\\begin{tabular}{lrrr}','\\hline','Method & FNR & Query distances & Cal. seconds \\\\','\\hline']
            for s in summary:
                if s['dataset']!=dataset or s['mode']!=mode or s['step']!=5:continue
                rr=[r for r in rows if r['dataset']==dataset and r['mode']==mode and r['method']==s['method']]
                times=[sum(r['cal_seconds'] for r in rr if r['seed']==seed) for seed in range(5)]
                sd=s['fnr_sd'] or 0
                snippet.append(f'{short_names[s["method"]]} & ${s["fnr_mean"]:.4f} \\pm {sd:.4f}$ & {s["distances_mean"]:.0f} & {np.mean(times):.3f} \\\\')
            snippet+=['\\hline','\\end{tabular}']
            (ROOT/f'table_{dataset}_{mode}.tex').write_text('\n'.join(snippet)+'\n')
    if (ROOT/'memory_profile.json').exists():
        memory=json.loads((ROOT/'memory_profile.json').read_text())['rows']
        lines+=['','## Diagnostic memory samples','',
            'Separate processes, seed 0, IID 60% to 65% corpus update. RSS sampled every 5ms; includes interpreter, data and index. Increments are relative to each process immediately before the kernel. These can miss brief peaks and are not exact peak-memory or serving measurements. A zero sampled increase can reflect allocator reuse or sampling resolution; it does not mean zero allocations.','',
            '| Dataset | Method | RSS before (MiB) | Sampled peak RSS (MiB) | Sampled increase (MiB) |',
            '|---|---|---:|---:|---:|']
        for m in memory:lines.append(f'| {m["dataset"]} | {m["method"]} | {m["rss_before_bytes"]/2**20:.2f} | {m["sampled_peak_rss_bytes"]/2**20:.2f} | {m["sampled_increment_bytes"]/2**20:.2f} |')
    lines+=['','## Scientific interpretation','',
       'The primary IID hypothesis passes only if replicated_failure_by_mode.iid is true. Boundary-late arrival is an engineered diagnostic and retraining changes geometry: even if either fails, it must not be reported as a failure of ordinary IID fixed-centroid ingestion. All counts and modes are retained in gate.json. No pilot-driven stress search or fresh-query validation has been done.','',
       'Cached full CRC must match full current-corpus calibration exactly; the harness asserts equal exact IDs, losses and selected budgets. Thus repeated full brute-force relabeling is not the strongest baseline. The 64/256/all-query ablations test a known calibration sample-size tradeoff, not a new update theorem. Exact-delta guarding has a deterministic insertion-only dominance argument but adds query work; it is a strong conservative control, not evidence that all conservative solutions require full search.','',
       'The prespecified rounded, high-gain feedback controller oscillated badly on image vectors. This is a negative finding about that heuristic, NOT a refutation of published Rolling Risk Control. Its separate feedback_instability figure and all raw outcomes are retained; it must not be used as a weakened stand-in for a faithful strong online baseline.','',
       '## Limits and pending evidence','',
       '- Small CPU IVF prototype; no faithful ConANN score, Quake, DARTH+ or graph-index reproduction. Coarse integer probe budgets can leave substantial initial risk slack, masking a failure that a tighter score-based policy might show. No claim that these systems fail or that all dynamic-index calibration is safe.',
       '- Corpus/query split seeds vary, but public queries have been explored in earlier work; no independent confirmation. Reserved queries remain unevaluated.',
       '- Engineered arrival order is not chronological production ingestion. Raw Fashion pixels are a second geometry, not modern dense retrieval embeddings.',
       '- Corpus-only ingestion/retraining, no deletions, mixed updates or query drift. An insertion-only guard does not establish deletion safety.',
       '- Calibration kernel times include exact labels/cache update and loss curves, excluding index build, data load, bootstrap, and final scalar budget selection. Vector-distance counts separately include calibration centroids in results.csv. Index build/mutation times are recorded separately.',
       '- Query work is replayed distance count, not observed serving latency. Add 64 centroid distances for IVF/guard; full exact search need not compute centroids.',
       '- The legacy cal_retained_bytes metric counts top-k label arrays produced by a kernel, not minimal persistent deployment memory. Only cache methods need to retain those arrays between updates. It excludes the raw audit-query matrix, corpus and index. The guard needs no new label arrays after initialization; aggregation corrects that derived accounting to zero. The legacy field cal_estimated_peak_workspace_bytes is normalized to cal_workspace_proxy_bytes: a selected-array proxy, NOT total/measured peak memory. Dtype conversion, allocator/BLAS and other temporaries add memory.',
       '- CRC expectation, Hoeffding population-risk confidence, cumulative feedback control and per-query safety are different guarantees. No anytime or distribution-free drift guarantee for the rounded feedback controller is claimed.',
       '- A discovery paper requires a real replicated failure, distinct contribution beyond standard cache/subsample/feedback repairs, matched-risk efficiency, fresh confirmation, another index family, serving latency/memory measurement and completed closest-work review. All remain pending unless separately documented.','',
       '## Attempt ledger','',
       '1. Frozen protocol, three mutation modes and failure thresholds before inspecting outcomes.',
       '2. Smoke-tested exact candidate recall, cache identity under insertions/ties and guard dominance.',
       '3. First unoptimized IID seed showed decreasing error. Replaced full sorting with an exact boundary-tie-aware top-k partition kernel and removed repeated float64 conversions; verified against stable full sorting. Interrupted preliminary sweep and regenerated ALL results with the same faster kernel for fair timing. No seed or mode was selected based on favorable outcomes.',
       '4. All calibration/evaluation truth is CURRENT-corpus truth. Cached update equality checked at every state.',
       '5. No paper draft or reserved-query evaluation. See gate.json for the mechanical stop decision.']
    lines+=['6. Added a synthetic boundary-crossing positive control after observing the exploratory negative trend: static FNR changes from 0 to 1, and recalibration selects exact search. This tests harness sensitivity, not a realistic replicated failure or novelty.',
       '7. Reused identical paired bootstrap resamples as count matrices and switched public CORPUS loading to contiguous reads to avoid h5py overhead. Completed runs were resumed without outcome filtering. Neither change alters queried vectors, distances, budgets, calibration kernels or scientific outcomes. The workspace estimate field was renamed as a proxy for accuracy; no measured values were changed.']
    (ROOT/'FINDINGS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    overview=['# Direction A — concise outcome','',
        '**Status: exploratory prototype; novelty not established.** No reserved final queries have been evaluated.','',
        '## Test and decision','',
        'Two public vector geometries, five independent corpus/index/query-split seeds, IID insertion plus two prespecified diagnostics (boundary-heavy arrivals and centroid retraining). Start at 60% corpus; evaluate 65%, 70%, 75%, 80% and 100%. k=10, alpha=.10, 64 IVF lists. A replicated failure requires FNR>.12, bootstrap lower bound>.10 and >.02 paired increase at two adjacent states in >=4/5 seeds on BOTH datasets.','',
        '| Mutation | Replicated failure gate |','|---|---|']
    for mode,value in replicated.items():overview.append(f'| {mode} | {value} |')
    overview+=['','## Primary IID static-CRC result','',
               '| Dataset | Initial mean FNR ± seed SD | 100%-corpus mean FNR ± seed SD |','|---|---:|---:|']
    for d in ['glove','fashion']:
        initial=next((s for s in summary if s['dataset']==d and s['mode']=='iid' and s['method']=='static_crc' and s['step']==0),None)
        final=next((s for s in summary if s['dataset']==d and s['mode']=='iid' and s['method']=='static_crc' and s['step']==5),None)
        if initial and final:overview.append(f'| {d} | {initial["fnr_mean"]:.4f} ± {(initial["fnr_sd"] or 0):.4f} | {final["fnr_mean"]:.4f} ± {(final["fnr_sd"] or 0):.4f} |')
    overview+=['','## Tested update and strongest control','',
        'Maintain exact calibration top-k by T_t(q)=TopK(T_(t-1)(q) union new_batch). Update current IVF losses, then choose the smallest p satisfying (1+sum_i loss_t(q_i,p))/(m+1)<=alpha. m=64 is the lightweight candidate; m=256 and m=1000 are ablations/controls. Full cached m=1000 produces exactly the same budgets and FNR as full brute-force recalibration. This is a standard incremental computation plus standard CRC, not a new algorithm.','',
        '| Dataset (IID) | Method | Final FNR | Final query distances | Calibration vector distances, summed over stream |','|---|---|---:|---:|---:|']
    for d in ['glove','fashion']:
        for method in ['static_crc','full_crc','cached_full_crc','audit64_crc','exact_delta_guard']:
            s=next((x for x in summary if x['dataset']==d and x['mode']=='iid' and x['step']==5 and x['method']==method),None)
            if not s:continue
            rr=[r for r in rows if r['dataset']==d and r['mode']=='iid' and r['method']==method]
            counts=[sum(r['cal_vector_distances'] for r in rr if r['seed']==seed) for seed in range(5)]
            overview.append(f'| {d} | {method} | {s["fnr_mean"]:.4f} | {s["distances_mean"]:.0f} | {np.mean(counts):.0f} |')
    overview+=['','## Meaning and limits','',
        'A changing corpus invalidates automatic transfer of a static certificate, but does not imply upward risk drift. With fixed Voronoi cells and locally supported IID arrivals, new neighbors can become more concentrated inside the query cell; an elementary binomial bound explaining this is in THEORY_AND_PRIOR_WORK.md. It is not claimed as a novel theorem.','',
        'If all failure gates are false, the required Phase-1 mechanism was not established and full experiments should stop. The code supplies a useful exact calibration-maintenance solution, but cannot turn this engineering reuse into a top-tier contribution. Quake already addresses dynamic vector indexing; generic online risk adaptation is also established.','',
        'All results are exploratory and small-scale. Cached/partial methods have pointwise mean-risk guarantees under their stated independence assumptions, not per-query or anytime guarantees. No faithful ConANN/Quake/DARTH+ reproduction, independent confirmation, HNSW/deletion study, total peak-memory or serving-latency benchmark is complete. Read FINDINGS.md for every state/method, uncertainty, calibration times, memory limits and attempted alternatives. Full-stage and paper results remain pending.']
    (ROOT/'OVERVIEW.md').write_text('\n'.join(overview)+'\n',encoding='utf-8')
    plots(summary)
    save(ROOT/'manifest.json',{str(p.relative_to(ROOT)):digest(p) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json'})
    print(json.dumps(dict(runs=len(runs),conditions=len(rows),replicated_failure=replicated)),flush=True)
def plots(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    modes=['iid','boundary','retrain'];fig,axes=plt.subplots(2,3,figsize=(12,6),sharey=True)
    for ax,(dataset,mode) in zip(axes.flat,[(d,m) for d in ['glove','fashion'] for m in modes]):
        for method in ['static_crc','full_crc','audit64_crc','audit256_crc','exact_delta_guard']:
            rr=sorted([s for s in summary if s['dataset']==dataset and s['mode']==mode and s['method']==method],key=lambda x:x['step'])
            if rr:ax.errorbar([s['fraction'] for s in rr],[s['fnr_mean'] for s in rr],yerr=[s['fnr_sd'] or 0 for s in rr],label=method,marker='.',capsize=2)
        ax.axhline(.1,color='black',ls='--');ax.set_ylim(bottom=0);ax.set_title(dataset+' / '+mode);ax.set_xlabel('Cumulative corpus fraction')
    axes[0,0].set_ylabel('FNR mean ± seed SD');axes[1,0].set_ylabel('FNR mean ± seed SD');axes[1,2].legend(fontsize=6)
    fig.tight_layout();fig.savefig(ROOT/'trajectories.png',dpi=180);fig.savefig(ROOT/'trajectories.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3.5),sharey=True)
    for ax,dataset in zip(axes,['glove','fashion']):
        for method in ['static_crc','full_crc','feedback64']:
            rr=sorted([s for s in summary if s['dataset']==dataset and s['mode']=='iid' and s['method']==method],key=lambda x:x['step'])
            ax.errorbar([s['fraction'] for s in rr],[s['fnr_mean'] for s in rr],yerr=[s['fnr_sd'] or 0 for s in rr],label=method,marker='.',capsize=2)
        ax.axhline(.1,color='black',ls='--');ax.set_ylim(bottom=0);ax.set_title(dataset+' / IID');ax.set_xlabel('Cumulative corpus fraction')
    axes[0].set_ylabel('FNR mean ± seed SD');axes[1].legend(fontsize=7)
    fig.tight_layout();fig.savefig(ROOT/'feedback_instability.png',dpi=180);fig.savefig(ROOT/'feedback_instability.pdf');plt.close(fig)
if __name__=='__main__':main()

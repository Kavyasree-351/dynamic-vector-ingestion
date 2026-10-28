"""Staged Direction-A experiments. All public final query vectors stay unused."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse,json,time
import numpy as np
from threadpoolctl import threadpool_limits
from data import ROOT,DATA,load,save
from index import IVF,full_topk,arrival_order,stable_small_topk
from calibration import Cache,choose,recompute
STATES=[.60,.65,.70,.75,.80,1.00]
BOOT_COUNTS={}
def interval(v,seed=123):
    key=(len(v),seed)
    if key not in BOOT_COUNTS:
        rng=np.random.default_rng(seed);ix=rng.integers(len(v),size=(2000,len(v)))
        BOOT_COUNTS[key]=np.stack([np.bincount(row,minlength=len(v)) for row in ix]).astype(float)
    return np.quantile(BOOT_COUNTS[key]@v/len(v),[.025,.975]).tolist()
def smoke():
    rng=np.random.default_rng(8);x=rng.normal(size=(140,5)).astype('f');x[100:104]=x[:4]
    tied=rng.integers(0,10,size=(100,140))
    assert np.array_equal(stable_small_topk(tied,10),np.argsort(tied,axis=1,kind='stable')[:,:10])
    q=rng.normal(size=(17,5)).astype('f');idx=IVF(8,1);idx.build(x[:84]);cache=Cache(q)
    initial,_=cache.update(x[:84],idx);p=choose(initial);original=initial[:,p];labels=idx.labels.copy();ranks=idx.ranks(q);centers=idx.centers.copy()
    for n in [84,100,140]:
        if n>len(idx.labels):idx.add(x[len(idx.labels):n])
        loss,_=cache.update(x[:n],idx);_,truth=full_topk(q,x[:n]);assert np.array_equal(cache.ids,truth)
        assert np.array_equal(centers,idx.centers)
        for budget in range(1,9):
            ann,work=idx.search(q,x[:n],budget)
            direct=np.array([1-len(set(a)&set(b))/10 for a,b in zip(ann,truth)])
            assert np.allclose(direct,loss[:,budget-1])
        is_new=truth>=84;safe=np.where(is_new,True,np.take_along_axis(ranks,labels[np.minimum(truth,83)],axis=1)<=p)
        assert np.all(1-safe.mean(1)<=original+1e-12)
    # Positive control: initial +1/-1 cells; queries just right of boundary;
    # newly arriving near-boundary LEFT vectors become the true neighbors.
    core=np.r_[np.full((10,1),-1.),np.full((10,1),1.)].astype('f')
    queries=np.full((100,1),.1,dtype='f');control=IVF(2,2);control.build(core)
    _,gt=full_topk(queries,core);before,_=control.curves(queries,gt);budget=choose(before)
    assert budget==0 and np.all(before[:,budget]==0)
    delta=np.full((10,1),-.01,dtype='f');mutated=np.r_[core,delta];control.add(delta)
    _,gt=full_topk(queries,mutated);after,_=control.curves(queries,gt)
    assert np.all(after[:,budget]==1) and choose(after)==1
    save(ROOT/'smoke.json',dict(passed=True,checks=['direct ANN vs trace recall every budget/state',
        'incremental vs full ground truth including duplicates/ties','insertion guard pointwise domination',
        'frozen-centroid invariance','nested loss','full-search zero FNR','synthetic positive-control static FNR 0 to 1'],
        positive_control=dict(synthetic=True,initial_fnr=0,mutated_fnr=1,not_a_real_data_failure=True)))
    print('Smoke passed',flush=True)
def run_one(name,seed,mode,data):
    begin=time.perf_counter();base,design,cal,pilot,prov=load(name,seed,data)
    order=arrival_order(base,mode,seed);base=base[order]
    prov['arrival_positions']=order.tolist();prov['mode']=mode
    core=int(.6*len(base));idx=IVF(64,seed);build=idx.build(base[:core])
    original_labels=idx.labels.copy();pilot_core_rank=idx.ranks(pilot)
    caches={n:Cache(cal[:n]) for n in [64,256,1000]}
    allrows=[];arrays={};static=None;controller=None;periodic=None;initial_loss=None;initial_work=None
    old=0
    for step,fraction in enumerate(STATES):
        n=int(fraction*len(base));x=base[:n];mutation_start=time.perf_counter()
        if step:
            if mode=='retrain':idx.build(x)
            else:idx.add(base[old:n])
        mutation_seconds=time.perf_counter()-mutation_start
        vals,truth,full_loss,full_meta=recompute(cal,x,idx)
        cache_losses={};cache_meta={}
        for size,cache in caches.items():cache_losses[size],cache_meta[size]=cache.update(x,idx)
        assert np.array_equal(caches[1000].ids,truth),'Cached labels must match full current-corpus truth'
        assert np.array_equal(cache_losses[1000],full_loss)
        _,pt=full_topk(pilot,x);loss,work=idx.curves(pilot,pt)
        if step==0:
            static=choose(full_loss);static_h=choose(full_loss,hoeffding=True);controller=static;periodic=static
            initial_loss=loss[:,static].copy();initial_work=work[:,static].copy()
        if step%2==0 or step==len(STATES)-1:periodic=choose(full_loss);periodic_meta=full_meta
        else:periodic_meta=dict(seconds=0,vector_distances=0,centroid_distances=0,retained_bytes=0,workspace_proxy_bytes=0)
        choices={'static_crc':static,'static_hoeffding':static_h,'full_crc':choose(full_loss),
            'periodic_crc':periodic,'cached_full_crc':choose(cache_losses[1000]),'audit64_crc':choose(cache_losses[64]),
            'audit256_crc':choose(cache_losses[256]),'feedback64':controller,'exact':63}
        for method,p in choices.items():
            meta=full_meta if method=='full_crc' else periodic_meta if method=='periodic_crc' else cache_meta[1000] if method=='cached_full_crc' else cache_meta[256] if method=='audit256_crc' else cache_meta[64] if method in ['audit64_crc','feedback64'] else full_meta if step==0 and method.startswith('static') else dict(seconds=0,vector_distances=0,centroid_distances=0,retained_bytes=0,workspace_proxy_bytes=0)
            v=loss[:,p];w=work[:,p];key=f'{step}__{method}';arrays[key+'__loss']=v;arrays[key+'__work']=w
            bounds=interval(v);drift=interval(v-initial_loss)
            allrows.append(dict(dataset=name,seed=seed,mode=mode,step=step,fraction=fraction,corpus_size=n,method=method,
                nprobe=p+1,fnr=float(v.mean()),ci_low=bounds[0],ci_high=bounds[1],drift=float((v-initial_loss).mean()),
                drift_ci_low=drift[0],drift_ci_high=drift[1],distances=float(w.mean()),**{'cal_'+k:v for k,v in meta.items()},
                build_seconds=build if step==0 else 0,mutation_seconds=mutation_seconds))
        # Exact delta merge into frozen initial IVF candidates; no mutated-index dependence.
        new=pt>=core;oldids=np.minimum(pt,core-1)
        caught=new|(np.take_along_axis(pilot_core_rank,original_labels[oldids],axis=1)<=static)
        guard=1-caught.mean(1);guard_work=initial_work+n-core
        assert np.all(guard<=initial_loss+1e-12)
        key=f'{step}__exact_delta_guard';arrays[key+'__loss']=guard;arrays[key+'__work']=guard_work
        ci=interval(guard);drift=interval(guard-initial_loss)
        allrows.append(dict(dataset=name,seed=seed,mode=mode,step=step,fraction=fraction,corpus_size=n,method='exact_delta_guard',
            nprobe=static+1,fnr=float(guard.mean()),ci_low=ci[0],ci_high=ci[1],drift=float((guard-initial_loss).mean()),
            drift_ci_low=drift[0],drift_ci_high=drift[1],distances=float(guard_work.mean()),
            cal_seconds=full_meta['seconds'] if step==0 else 0,cal_vector_distances=full_meta['vector_distances'] if step==0 else 0,
            cal_centroid_distances=full_meta['centroid_distances'] if step==0 else 0,
            cal_retained_bytes=full_meta['retained_bytes'] if step==0 else 0,cal_workspace_proxy_bytes=0,
            build_seconds=build if step==0 else 0,mutation_seconds=0))
        feedback=cache_losses[64][:,controller].mean();controller=int(np.clip(controller+np.ceil(64*(feedback-.1)),0,63))
        old=n
    output=ROOT/'results';output.mkdir(exist_ok=True)
    prefix=f'{name}_{mode}_{seed}'
    save(output/(prefix+'_metrics.json'),dict(rows=allrows,total_seconds=time.perf_counter()-begin))
    save(output/(prefix+'_provenance.json'),prov)
    np.savez_compressed(output/(prefix+'_paired.npz'),**arrays)
    main=[round(r['fnr'],4) for r in allrows if r['method']=='static_crc']
    print(name,mode,seed,'static CRC:',main,flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['smoke','pilot','full']);p.add_argument('--data',type=__import__('pathlib').Path,default=DATA)
    p.add_argument('--resume',action='store_true',help='Skip only fully saved runs; never selects by outcome')
    p.add_argument('--datasets',nargs='+',default=['glove','fashion'],choices=['glove','fashion']);p.add_argument('--seeds',nargs='+',type=int,default=list(range(5)))
    p.add_argument('--modes',nargs='+',default=['iid','boundary','retrain'],choices=['iid','boundary','retrain']);a=p.parse_args()
    with threadpool_limits(limits=1):
        if a.action=='smoke':smoke();return
        if a.action=='full':raise SystemExit('Full experiment blocked: requires distinct-contribution clearance, frozen independent confirmation and passed pilot gate. No reserved data opened.')
        assert json.loads((ROOT/'smoke.json').read_text())['passed'],'Run smoke first'
        for name in a.datasets:
            for mode in a.modes:
                for seed in a.seeds:
                    prefix=ROOT/'results'/f'{name}_{mode}_{seed}'
                    complete=all(__import__('pathlib').Path(str(prefix)+suffix).exists() for suffix in ['_metrics.json','_provenance.json','_paired.npz'])
                    if a.resume and complete:continue
                    run_one(name,seed,mode,a.data)
if __name__=='__main__':main()

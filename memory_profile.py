"""Isolated-process 5ms RSS samples for one +5%-corpus calibration update.

Diagnostic sampling, not an exact peak-memory/serving benchmark. Uses seed 0
and only existing exploratory calibration queries. No final queries accessed.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse,json,subprocess,sys,threading,time
import psutil
from threadpoolctl import threadpool_limits
from data import ROOT,DATA,load,save
from index import IVF,arrival_order
from calibration import Cache,recompute
def one(dataset,method):
    base,_,cal,_,_=load(dataset,0,DATA);base=base[arrival_order(base,'iid',0)]
    core=int(.6*len(base));current=int(.65*len(base));index=IVF(64,0);index.build(base[:core])
    if method!='full_crc':
        cache=Cache(cal[:64] if method=='audit64_crc' else cal)
        cache.update(base[:core],index)
    index.add(base[core:current]);process=psutil.Process();samples=[];stop=threading.Event()
    def sample():
        while not stop.is_set():
            samples.append(process.memory_info().rss);stop.wait(.005)
    before=process.memory_info().rss;thread=threading.Thread(target=sample,daemon=True);thread.start();t=time.perf_counter()
    try:
        if method=='full_crc':recompute(cal,base[:current],index)
        else:cache.update(base[:current],index)
    finally:
        elapsed=time.perf_counter()-t;samples.append(process.memory_info().rss);stop.set();thread.join()
    peak=max(samples+[before])
    return dict(dataset=dataset,seed=0,mode='iid',method=method,initial_fraction=.6,current_fraction=.65,
        rss_before_bytes=before,sampled_peak_rss_bytes=peak,sampled_increment_bytes=peak-before,
        samples=len(samples),sample_period_ms=5,elapsed_seconds=elapsed,
        limitation='Sampled process RSS, includes interpreter/data/index; may miss short peaks; one configuration, not serving memory.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--one',action='store_true');p.add_argument('--dataset',choices=['glove','fashion']);p.add_argument('--method',choices=['full_crc','cached_full_crc','audit64_crc']);a=p.parse_args()
    if a.one:
        with threadpool_limits(limits=1):print(json.dumps(one(a.dataset,a.method)))
    else:
        rows=[]
        for dataset in ['glove','fashion']:
            for method in ['full_crc','cached_full_crc','audit64_crc']:
                done=subprocess.run([sys.executable,str(ROOT/'memory_profile.py'),'--one','--dataset',dataset,'--method',method],capture_output=True,text=True,check=True)
                row=json.loads(done.stdout);rows.append(row);print(dataset,method,row['sampled_increment_bytes'],flush=True)
        save(ROOT/'memory_profile.json',dict(rows=rows,final_queries_evaluated=False))
if __name__=='__main__':main()

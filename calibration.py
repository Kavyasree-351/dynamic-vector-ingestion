"""Known calibration and exact-cache baselines. No invented guarantees."""
import time
import numpy as np
from index import full_topk,update_topk
def choose(loss,alpha=.1,hoeffding=False,delta=.05):
    bound=loss.mean(axis=0)+np.sqrt(np.log(loss.shape[1]/delta)/(2*len(loss))) if hoeffding else (loss.sum(axis=0)+1)/(len(loss)+1)
    valid=np.flatnonzero(bound<=alpha)
    return int(valid[0]) if len(valid) else loss.shape[1]-1
def recompute(q,x,index,k=10):
    start=time.perf_counter();values,ids=full_topk(q,x,k);loss,_=index.curves(q,ids)
    return values,ids,loss,dict(seconds=time.perf_counter()-start,vector_distances=len(q)*len(x),
        centroid_distances=len(q)*index.nlist,retained_bytes=values.nbytes+ids.nbytes,
        workspace_proxy_bytes=32*len(x)*16+len(q)*index.nlist*k*8)
class Cache:
    def __init__(self,q,k=10):self.q=q;self.k=k;self.n=0
    def update(self,x,index):
        start=time.perf_counter();old=self.n
        if old==0:self.values,self.ids=full_topk(self.q,x,self.k)
        else:self.values,self.ids=update_topk(self.q,x[old:],old,self.values,self.ids,self.k)
        self.n=len(x);loss,_=index.curves(self.q,self.ids)
        meta=dict(seconds=time.perf_counter()-start,vector_distances=len(self.q)*(self.n-old),
            centroid_distances=len(self.q)*index.nlist,retained_bytes=self.values.nbytes+self.ids.nbytes,
            workspace_proxy_bytes=32*(self.n-old+self.k)*16+len(self.q)*index.nlist*self.k*8)
        return loss,meta

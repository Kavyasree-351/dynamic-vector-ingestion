"""Exact-within-list IVF, deterministic current-corpus ground truths and traces."""
import time
import numpy as np
from sklearn.cluster import MiniBatchKMeans
def distances(q,x):
    q=np.asarray(q,dtype=np.float64);x=np.asarray(x,dtype=np.float64)
    return np.maximum((q*q).sum(1)[:,None]+(x*x).sum(1)[None,:]-2*q@x.T,0)
class IVF:
    def __init__(self,nlist=64,seed=0):self.nlist=nlist;self.seed=seed
    def build(self,x):
        t=time.perf_counter();self.model=MiniBatchKMeans(n_clusters=self.nlist,random_state=self.seed,n_init=3,batch_size=1024,max_iter=100)
        self.labels=self.model.fit_predict(x);self.centers=self.model.cluster_centers_.copy();return time.perf_counter()-t
    def add(self,x):self.labels=np.r_[self.labels,self.model.predict(x)]
    def ranks(self,q):return np.argsort(np.argsort(distances(q,self.centers),axis=1,kind='stable'),axis=1)
    def curves(self,q,truth):
        ranks=self.ranks(q);tr=np.take_along_axis(ranks,self.labels[truth],axis=1)
        loss=1-(tr[:,:,None]<=np.arange(self.nlist)).mean(axis=1)
        sizes=np.bincount(self.labels,minlength=self.nlist)
        work=np.cumsum(sizes[np.argsort(ranks,axis=1)],axis=1)
        assert np.all(np.diff(loss,axis=1)<=1e-12) and np.all(loss[:,-1]==0)
        return loss,work
    def search(self,q,x,p,k=10):
        """Actual IVF retrieval for smoke/serving checks, no truth access."""
        out=[];work=[];rank=self.ranks(q)
        for i,query in enumerate(q):
            ids=np.flatnonzero(rank[i,self.labels]<p);d=distances(query[None,:],x[ids])[0]
            out.append(ids[np.argsort(d,kind='stable')[:k]]);work.append(len(ids))
        return out,np.array(work)
def full_topk(q,x,k=10,block=32):
    q=np.asarray(q,dtype=np.float64);x=np.asarray(x,dtype=np.float64)
    ids=[];values=[]
    for lo in range(0,len(q),block):
        d=distances(q[lo:lo+block],x);j=stable_small_topk(d,k)
        ids.append(j);values.append(np.take_along_axis(d,j,axis=1))
    return np.concatenate(values),np.concatenate(ids)
def update_topk(q,batch,offset,old_values,old_ids,k=10,block=32):
    q=np.asarray(q,dtype=np.float64);batch=np.asarray(batch,dtype=np.float64)
    values=[];ids=[]
    for lo in range(0,len(q),block):
        d=distances(q[lo:lo+block],batch)
        v=np.c_[old_values[lo:lo+len(d)],d]
        ix=np.c_[old_ids[lo:lo+len(d)],np.broadcast_to(np.arange(offset,offset+len(batch)),d.shape)]
        # Existing tied IDs precede all newly inserted IDs; old cache ties are sorted.
        j=stable_small_topk(v,k)
        values.append(np.take_along_axis(v,j,axis=1));ids.append(np.take_along_axis(ix,j,axis=1))
    return np.concatenate(values),np.concatenate(ids)
def stable_small_topk(d,k):
    """Partition plus explicit boundary ties; same output as stable full sort."""
    cut=np.partition(d,k-1,axis=1)[:,k-1];out=[]
    for row,c in zip(d,cut):
        low=np.flatnonzero(row<c);eq=np.flatnonzero(row==c)[:k-len(low)]
        candidates=np.r_[low,eq]
        out.append(candidates[np.argsort(row[candidates],kind='stable')])
    return np.stack(out)
def arrival_order(x,mode,seed):
    rng=np.random.default_rng(23000+seed)
    if mode!='boundary':return rng.permutation(len(x))
    # Engineered workload uses only corpus geometry, never evaluation queries.
    aux=MiniBatchKMeans(n_clusters=64,random_state=seed+200,n_init=3,batch_size=1024,max_iter=100).fit(x)
    d=np.sort(distances(x,aux.cluster_centers_),axis=1)[:,:2]
    ambiguity=d[:,0]/np.maximum(d[:,1],1e-12)
    return np.argsort(ambiguity,kind='stable')

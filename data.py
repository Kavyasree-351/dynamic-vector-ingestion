"""Public inputs and permanently separated exploratory/reserved query IDs."""
import gzip,hashlib,json
from pathlib import Path
import h5py
import numpy as np
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'work'/'datasets'
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for x in iter(lambda:f.read(1048576),b''):h.update(x)
    return h.hexdigest()
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2),encoding='utf-8')
def load(name,seed,data=DATA):
    previous=json.loads((ROOT/'inputs'/f'{name}.json').read_text())
    for file,expected in previous['files'].items():
        assert digest(data/file)==expected,'Public data bytes changed: '+file
    pool=np.array(previous['design_ids']+previous['calibration_ids']+previous['pilot_ids'])
    rng=np.random.default_rng(17000+seed);used=rng.permutation(pool)
    if name=='glove':
        with h5py.File(data/'glove-25-angular.hdf5') as f:
            bi=np.sort(rng.choice(len(f['train']),20000,replace=False))
            # Reading the public corpus contiguously avoids h5py's expensive
            # large fancy-index selection; reserved QUERY vectors stay unread.
            base=np.asarray(f['train'],dtype='f')[bi];o=np.argsort(used)
            query=np.asarray(f['test'][used[o]],dtype='f')[np.argsort(o)]
        base/=np.maximum(np.linalg.norm(base,axis=1,keepdims=True),1e-12)
        query/=np.maximum(np.linalg.norm(query,axis=1,keepdims=True),1e-12)
    else:
        def images(path):
            with gzip.open(path,'rb') as f:
                head=np.frombuffer(f.read(16),dtype='>u4');assert head[0]==2051
                return np.frombuffer(f.read(),dtype='u1').reshape(int(head[1]),-1)
        bi=np.sort(rng.choice(60000,10000,replace=False))
        # Integer-valued float32 pixels give exact float64 squared distances;
        # uniform scaling is immaterial to Euclidean neighbor order.
        base=images(data/'train-images-idx3-ubyte.gz')[bi].astype('f')
        query=images(data/'t10k-images-idx3-ubyte.gz')[used].astype('f')
    reserved=set(previous['reserved_unevaluated_ids']);assert not(set(used)&reserved)
    assert len(set(used))==2000
    provenance=dict(dataset=name,seed=seed,files=previous['files'],base_size=len(base),dimension=base.shape[1],
        corpus_ids=bi.tolist(),design_ids=used[:400].tolist(),calibration_ids=used[400:1400].tolist(),
        pilot_ids=used[1400:].tolist(),reserved_unevaluated_ids=sorted(reserved))
    return base,query[:400],query[400:1400],query[1400:],provenance

"""Validate all saved outcomes and paired accounting, never fresh queries."""
import json
import numpy as np
from data import ROOT,save
def main():
    runs=0;conditions=0;seen=set()
    for path in sorted((ROOT/'results').glob('*_metrics.json')):
        prefix=path.name.replace('_metrics.json','');obj=json.loads(path.read_text());rr=obj['rows']
        provenance=json.loads((ROOT/'results'/(prefix+'_provenance.json')).read_text())
        seen.add((provenance['dataset'],provenance['mode'],provenance['seed']))
        assert len(set(provenance['corpus_ids']))==provenance['base_size']
        assert sorted(provenance['arrival_positions'])==list(range(provenance['base_size']))
        splits=[set(provenance[k]) for k in ['design_ids','calibration_ids','pilot_ids','reserved_unevaluated_ids']]
        assert [len(s) for s in splits[:3]]==[400,1000,600]
        assert all(not(a&b) for i,a in enumerate(splits) for b in splits[i+1:])
        raw=np.load(ROOT/'results'/(prefix+'_paired.npz'))
        assert len(rr)==60
        for r in rr:
            key=f'{r["step"]}__{r["method"]}';v=raw[key+'__loss'];w=raw[key+'__work']
            assert len(v)==len(w)==600
            assert np.all((v>=0)&(v<=1)) and np.all((w>=0)&(w<=r['corpus_size']))
            assert abs(v.mean()-r['fnr'])<1e-12 and abs(w.mean()-r['distances'])<1e-9
            if r['method']=='exact':assert np.all(v==0) and np.all(w==r['corpus_size'])
            if r['method']=='cached_full_crc':
                ref=next(x for x in rr if x['method']=='full_crc' and x['step']==r['step'])
                assert r['nprobe']==ref['nprobe'] and r['fnr']==ref['fnr'] and r['distances']==ref['distances']
            if r['method']=='exact_delta_guard':assert np.all(v<=raw['0__static_crc__loss']+1e-12)
            conditions+=1
        runs+=1
    assert runs==30,'All two datasets, three modes and five seeds required'
    assert seen=={(d,m,s) for d in ['glove','fashion'] for m in ['iid','boundary','retrain'] for s in range(5)}
    save(ROOT/'validation.json',dict(passed=True,runs=runs,conditions=conditions,checks=['all five seeds and modes',
        'query split and reserved-pool separation','raw-summary consistency','cached/full budget equality',
        'insertion-guard pointwise domination','full-search exactness','loss/cost ranges']))
    print('Validated',runs,'runs;',conditions,'conditions.')
if __name__=='__main__':main()

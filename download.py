"""Public downloads pinned by the exact previously verified input hashes."""
import argparse,json,urllib.request
from data import ROOT,DATA,digest
p=argparse.ArgumentParser();p.add_argument('--data',type=__import__('pathlib').Path,default=DATA);args=p.parse_args();args.data.mkdir(parents=True,exist_ok=True)
urls={'glove-25-angular.hdf5':'https://huggingface.co/datasets/hhy3/ann-datasets/resolve/0bc1ed6/glove-25-angular.hdf5',
 'train-images-idx3-ubyte.gz':'https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/train-images-idx3-ubyte.gz',
 't10k-images-idx3-ubyte.gz':'https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/t10k-images-idx3-ubyte.gz'}
expected={}
for path in (ROOT/'inputs').glob('*.json'):expected.update(json.loads(path.read_text())['files'])
for name,url in urls.items():
    target=args.data/name
    if not target.exists():
        part=target.with_suffix(target.suffix+'.part');urllib.request.urlretrieve(url,part);part.replace(target)
    assert digest(target)==expected[name],f'Checksum mismatch: {name}'
    print(name,digest(target))

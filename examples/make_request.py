"""Write a hash-bound +0.5 EV public compositing request for create_fixture.py."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--fixture', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
fixture = json.loads(Path(args.fixture).read_text(encoding='utf-8-sig'))
output = Path(args.output).resolve()
if output.exists():
    raise RuntimeError('Output exists; choose a new request path.')
for key in ('source', 'image'):
    d = fixture[key]
    if hashlib.sha256(Path(d['file']).read_bytes()).hexdigest() != d['expected_sha256']:
        raise RuntimeError('Fixture changed: '+key)
request = {'schema_version': '1.0', 'command': 'compositing.run', 'params': {
    **fixture['source'], 'resources': [fixture['image']],
    'manifest': {'workflow_version': '1.1', 'workflow_id': 'PublicExample', 'scene': fixture['scene'],
                 'view_layer': fixture['view_layer'], 'operation': 'create', 'frame': 1,
                 'source': {'kind': 'image', **fixture['image'], 'colorspace': fixture['colorspace'], 'alpha_mode': fixture['alpha_mode']},
                 'components': [{'id': 'lift', 'kind': 'exposure', 'params': {'ev': 0.5}}]},
    'preview': {'width': 128, 'height': 128, 'samples': 1, 'engine': 'CYCLES', 'device': {'backend': 'CPU'},
                'compositor_device': 'CPU', 'allow_cpu_fallback': False, 'precision': 'FULL', 'baseline': True},
    'implementation_sha256': '9566cec1c2a9bf6db34c3085d964806b8ce7bafed1e0ae145bbb5259d655e629'}}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(request, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'request': str(output), 'command': request['command']}))

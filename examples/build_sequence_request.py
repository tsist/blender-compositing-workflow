"""Portable request builder. All project/data/output paths are caller supplied.

Pure JSON/contract preparation only; it never runs Blender or a producer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--cli-root', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
sub = parser.add_subparsers(dest='mode', required=True)
create = sub.add_parser('create')
create.add_argument('--frames', required=True, type=Path)
create.add_argument('--recipe', required=True, type=Path)
inspect = sub.add_parser('inspect')
inspect.add_argument('--bundle', required=True, type=Path)
inspect.add_argument('--order', required=True)
resume = sub.add_parser('resume')
resume.add_argument('--request', required=True, type=Path)
resume.add_argument('--authority', required=True, type=Path)
resume.add_argument('--worker-seconds', type=int)
args = parser.parse_args()
for name, value in vars(args).items():
    if isinstance(value, Path) and not value.is_absolute():
        parser.error(name + ' must be an absolute path')
sys.path.insert(0, str(args.cli_root / 'tools/blenderctl'))
from compositing_relight_sequence_contract import loads_strict, input_descriptors
from protocol import validate

def read(path):
    return loads_strict(path.read_bytes())

def descriptor(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return {'file': str(path), 'expected_sha256': h.hexdigest()}

if args.mode == 'create':
    manifest, recipe = read(args.frames), read(args.recipe)
    if set(recipe) & {'source', 'frames', 'resources'}:
        parser.error('recipe excludes source/frames/resources; these come from the frame manifest')
    params = {**recipe, 'source': manifest['source'], 'frames': manifest['frames'], 'resources': []}
elif args.mode == 'inspect':
    params = {'depth_sequence_version': '1.0', 'mode': 'inspect', 'bundle': descriptor(args.bundle),
              'frame_order': [int(value) for value in args.order.split(',')], 'resources': []}
else:
    old = validate(read(args.request))
    if old['command'] != 'compositing.depth-sequence' or old['params']['mode'] != 'create':
        parser.error('resume needs the original create request')
    params = old['params']
    prior_resume = params.get('resume')
    params['resources'] = [d for d in params['resources'] if d != prior_resume]
    params['resume'] = descriptor(args.authority)
    if args.worker_seconds is not None:
        params['budget']['timeout_seconds'] = args.worker_seconds
    params['resources'].append(params['resume'])
if args.mode != 'resume':
    params['resources'] = list({d['file']: d for d in input_descriptors(params)}.values())
request = validate({'schema_version': '1.0', 'command': 'compositing.depth-sequence', 'params': params})
with args.out.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(request, stream, indent=2, ensure_ascii=False, allow_nan=False)
    stream.write('\n')
print(json.dumps({'status': 'normalized_only', 'request': str(args.out),
                  'frame_count': len(params.get('frames', [])), 'runtime_admission': 'not_run'}))

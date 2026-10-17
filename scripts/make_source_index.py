"""Write a new finite-helper source index from an explicitly reviewed public tree.

This records bytes; it does not review, approve or run those sources.
"""
import argparse,hashlib,json
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cli-root',required=True,type=Path)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
if not args.cli_root.is_absolute() or not args.output.is_absolute():parser.error('Explicit absolute paths required')
root=args.cli_root.resolve(strict=True)
files=sorted(p for folder in ('tools/blenderctl','tools/compositing_workflow_addon') for p in (root/folder).rglob('*.py') if '__pycache__' not in p.parts)
rows=[]
for p in files:
    if p.is_symlink() or not p.resolve().is_relative_to(root):raise ValueError('Source link escaped root')
    rows.append({'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with args.output.open('x',encoding='utf-8',newline='\n') as stream:
    json.dump({'schema':'relight-helper-source-index-v1','files':rows},stream,indent=2);stream.write('\n')
print(json.dumps({'status':'indexed_unreviewed_bytes','files':len(rows)}))

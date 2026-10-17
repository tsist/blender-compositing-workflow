"""Static source-only checks; no Blender/GPU or visual certification."""
from __future__ import annotations
import ast,hashlib,json,posixpath,re,sys,tomllib
from pathlib import Path,PurePosixPath
from urllib.parse import unquote,urlsplit
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ADDON='tools/compositing_workflow_addon/'
ADDON_FILES=tuple(sorted(('__init__.py','contract.py','core.py','movie_contract.py','depth_contract.py','depth_estimate_contract.py','depth_math.py','relight_preview_ui.py','blender_manifest.toml','LICENSE','README.md')))
REFERENCE_PAIRS={x:x for x in ('usage','contract','validation','dependencies','color-hdr','licensing','depth-data','rgb-estimate','depth-relight','relight-session','imported-normal','depth-sequence','finite-relight-study')}
BLOCKED_PARTS={'.git','runtime','audit','__pycache__','.venv','venv','site-packages','dist-info'}
TEXT_SUFFIXES={'.py','.json','.md','.txt','.toml','.ps1','.yml','.yaml'}
def sha(data):return hashlib.sha256(data).hexdigest()
def safe_file(root,name):
    pure=PurePosixPath(name)
    if not name or '\\' in name or pure.is_absolute() or ':' in name or any(p in BLOCKED_PARTS or p in {'','..'} for p in pure.parts):raise ValueError('Unsafe publication path: '+name)
    path=root.joinpath(*pure.parts)
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):raise ValueError('Missing/nonregular publication file: '+name)
    if path.suffix not in TEXT_SUFFIXES and path.name not in {'LICENSE','.gitignore','.gitattributes'}:raise ValueError('Non-source publication member: '+name)
    return path
def load_publication(root):return json.loads((root/'PUBLICATION.json').read_text(encoding='utf-8-sig'))
def publication_rows(publication):
    rows=[]
    for key in ('runtime_documents','schema_documents','support_documents','public_documents'):
        values=publication.get(key)
        if not isinstance(values,list) or not values:raise ValueError('Missing nonempty inventory: '+key)
        rows.extend(values)
    return rows
def release_files(publication):return sorted(['PUBLICATION.json']+[x['file'] for x in publication_rows(publication)])
def private_findings(text):
    normal=text.replace('\\\\','/').replace('\\','/').lower();found=[]
    if ('173'+'99') in normal:found.append('private user identifier')
    if ('f:'+'/blender ai') in normal:found.append('private author project')
    pattern=r'wm-20\d\d-\d\d-\d\d-[a-z]|'+('runtime'+'/audit/')+r'|/\.'+'dsh/memory-lancedb-pro/'+r'|/\.'+'codex/(?:plugins|visualizations)/'
    if re.search(pattern,normal):found.append('private task/audit/store')
    if any(re.search(p,text) for p in (r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{40,}',r'sk-[A-Za-z0-9_-]{32,}',r'AKIA[A-Z0-9]{16}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')):found.append('credential-shaped value')
    return found
def anchors(text):
    result=set();counts={}
    for line in text.splitlines():
        match=re.match(r'^#{1,6}\s+(.+?)\s*#*$',line)
        if not match:continue
        title=re.sub(r'[`*_~]','',match[1]).strip().lower()
        title=re.sub(r'[^\w\- ]','',title,flags=re.UNICODE).replace(' ','-')
        number=counts.get(title,0);counts[title]=number+1
        result.add(title+('-'+str(number) if number else ''))
    result.update(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)',text,re.I))
    return result
def check_links(root,names):
    allowed=set(names);count=0
    for name in names:
        if not name.endswith('.md'):continue
        text=(root/name).read_text(encoding='utf-8-sig')
        targets=re.findall(r'\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+["\'][^)]*)?\)',text)
        targets+=re.findall(r'^\s*\[[^\]]+\]:\s*(<[^>]*>|\S+)',text,re.M)
        for raw in targets:
            value=raw.strip('<>');parsed=urlsplit(value)
            if parsed.scheme in {'https','http','mailto'}:continue
            if parsed.scheme or parsed.netloc:raise ValueError('Unsupported link scheme: '+name+' -> '+value)
            link=unquote(parsed.path);target=((root/name).parent/link).resolve() if link else (root/name).resolve()
            if not target.is_relative_to(root.resolve()):raise ValueError('Link escapes archive: '+name+' -> '+value)
            # Check lexical spelling as well as resolved existence: Windows must
            # not conceal a link that fails on a case-sensitive installed tree.
            rel=posixpath.normpath(posixpath.join(posixpath.dirname(name),link)) if link else name
            if rel not in allowed or not target.is_file() or target.is_symlink():raise ValueError('Missing packaged link: '+name+' -> '+value)
            if parsed.fragment and (target.suffix!='.md' or unquote(parsed.fragment) not in anchors(target.read_text(encoding='utf-8-sig'))):raise ValueError('Missing link anchor: '+name+' -> '+value)
            count+=1
    return count
def literal_assignment(path,name):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'))
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
def runtime_rows(root):
    paths=set((root/'tools/blenderctl').glob('*.py'))|set((root/ADDON).glob('*.py'))|{root/ADDON/'blender_manifest.toml'}
    return [{'file':p.relative_to(root).as_posix(),'expected_sha256':sha(p.read_bytes())} for p in sorted(paths)]
def verify(root=ROOT):
    root=root.resolve();pub=load_publication(root);rows=publication_rows(pub);seen={}
    for row in rows:
        name=row['file'];expected=row['expected_sha256']
        if name in seen:raise ValueError('Duplicate inventory member: '+name)
        if not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('Invalid SHA: '+name)
        data=safe_file(root,name).read_bytes()
        if sha(data)!=expected or type(row.get('bytes')) is not int or row['bytes']!=len(data):raise ValueError('SHA/byte count mismatch: '+name)
        seen[name]=expected
    names=release_files(pub)
    entries=list(root.rglob('*'))
    relevant=[p for p in entries if p.relative_to(root).parts[0] not in {'.git','dist'} and '__pycache__' not in p.relative_to(root).parts]
    if any(p.is_symlink() for p in relevant):raise ValueError('Source namespace contains a symlink')
    actual={p.relative_to(root).as_posix() for p in relevant if p.is_file()}
    if actual!=set(names):raise ValueError('Source namespace differs: '+str({'extra':sorted(actual-set(names)),'missing':sorted(set(names)-actual)}))
    runtime=runtime_rows(root)
    frozen=[{k:r[k] for k in ('file','expected_sha256')} for r in pub['runtime_documents']]
    if runtime!=frozen:raise ValueError('Runtime exact set or member bytes differ')
    identity=sha(json.dumps(runtime,sort_keys=True,separators=(',',':')).encode())
    if identity!=pub['runtime_identity']:raise ValueError('Implementation aggregate mismatch')
    schemas={p.relative_to(root).as_posix() for p in (root/'docs/cli/schemas').glob('*.json')}
    if schemas!={r['file'] for r in pub['schema_documents']}:raise ValueError('Schema exact namespace differs')
    support={p.relative_to(root).as_posix() for p in (root/'tools/geometry_nodes_workflow_addon').glob('*') if p.is_file()}
    support|={p.relative_to(root).as_posix() for p in (root/'tools/blender').glob('*') if p.is_file()}
    if support!={r['file'] for r in pub['support_documents']}:raise ValueError('Support exact namespace differs')
    native={p.name for p in (root/ADDON).iterdir() if p.is_file()}
    if native!=set(ADDON_FILES):raise ValueError('Native exact eleven-member namespace differs')
    if sha((root/'LICENSE').read_bytes())!='3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986' or (root/'LICENSE').read_bytes()!=(root/ADDON/'LICENSE').read_bytes():raise ValueError('Complete reviewed GPL text required')
    cli=literal_assignment(root/'tools/blenderctl/protocol.py','VERSION')
    manifest=tomllib.loads((root/ADDON/'blender_manifest.toml').read_text(encoding='utf-8'))
    info=literal_assignment(root/ADDON/'__init__.py','bl_info')
    if cli!=pub['cli'] or manifest['version']!=pub['addon'] or info['version']!=tuple(map(int,pub['addon'].split('.'))):raise ValueError('CLI/addon declared version mismatch')
    if manifest['id']!='compositing_workflow_addon' or manifest['license']!=['SPDX:GPL-3.0-or-later']:raise ValueError('Native manifest id/license mismatch')
    counts={'python_ast':0,'json_parse':0,'toml_parse':0,'text_privacy_scan':0}
    for name in names:
        p=safe_file(root,name);text=p.read_text(encoding='utf-8-sig');findings=private_findings(text)
        if findings:raise ValueError('Private content in '+name+': '+', '.join(findings))
        counts['text_privacy_scan']+=1
        if p.suffix=='.py':ast.parse(text,filename=name);counts['python_ast']+=1
        if p.suffix=='.json':json.loads(text);counts['json_parse']+=1
        if p.suffix=='.toml':tomllib.loads(text);counts['toml_parse']+=1
    for low in REFERENCE_PAIRS:
        if (root/'docs'/(low+'.md')).read_bytes()!=(root/'skills/blender-compositing/references'/(low+'.md')).read_bytes():raise ValueError('Reference copy differs: '+low)
    skills=[x for x in names if x.endswith('/SKILL.md')]
    if skills!=['skills/blender-compositing/SKILL.md']:raise ValueError('Exactly one portable skill required')
    skill=(root/skills[0]).read_text(encoding='utf-8-sig')
    if not skill.startswith('---\n') or not re.search(r'^name: blender-compositing\s*$',skill,re.M) or identity not in skill:raise ValueError('Skill name/frontmatter/runtime identity mismatch')
    if pub['skill']!=pub['release'] or pub['addon']!=pub['release']:raise ValueError('Declared release/skill/native version mismatch')
    index=json.loads((root/'skills/blender-compositing/source-index.json').read_text())
    expected=[{'path':r['file'],'sha256':r['expected_sha256']} for r in runtime if r['file'].endswith('.py')]
    if index!={'schema':'relight-helper-source-index-v1','files':expected}:raise ValueError('Finite helper public source index differs')
    return {'status':'passed_static_release_checks','runtime_files':len(runtime),'runtime_identity':identity,'schema_files':len(schemas),'support_files':len(support),'release_files':len(names),'markdown_links':check_links(root,names),'reference_pairs':len(REFERENCE_PAIRS),**counts,'scope':'Static source/hash/version/navigation/privacy only; no runtime or visual certification'}
if __name__=='__main__':
    try:print(json.dumps(verify(),indent=2))
    except (ValueError,OSError,KeyError,SyntaxError,TypeError,StopIteration) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);sys.exit(1)

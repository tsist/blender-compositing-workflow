"""Independently extract and inspect each of the three source-only archives."""
from __future__ import annotations
import argparse,ast,json,sys,zipfile
from pathlib import Path,PurePosixPath
sys.dont_write_bytecode=True
from verify_release import ADDON_FILES,check_links,private_findings,sha,verify
def verify_archives(dist,work):
    dist=dist.resolve(strict=True);work=work.resolve()
    if work.exists():raise ValueError('Use a new independent unpack directory')
    index=json.loads((dist/'release-index.json').read_text(encoding='utf-8'))
    if len(index['artifacts'])!=3:raise ValueError('Exactly three artifacts required')
    artifacts=index['artifacts']
    if len({x['file'] for x in artifacts})!=3:raise ValueError('Duplicate archive identity')
    expected_sums=''.join(x['sha256']+'  '+x['file']+'\n' for x in sorted(artifacts,key=lambda x:x['file']))
    if (dist/'SHA256SUMS').read_bytes()!=expected_sums.encode():raise ValueError('SHA256SUMS differs from exact artifact set')
    work.mkdir(parents=True,exist_ok=False);results=[];trees={}
    for i,item in enumerate(artifacts):
        name=item['file']
        if Path(name).name!=name or not name.endswith('.zip'):raise ValueError('Unsafe archive filename')
        path=dist/name;data=path.read_bytes()
        if sha(data)!=item['sha256'] or len(data)!=item['bytes']:raise ValueError('Archive SHA/size differs: '+name)
        if Path(item['member_index']).name!=item['member_index']:raise ValueError('Unsafe member index filename')
        members=json.loads((dist/item['member_index']).read_text(encoding='utf-8'))
        if members['archive']!=name or members['sha256']!=sha(data) or members['bytes']!=len(data):raise ValueError('Member index/archive identity mismatch')
        rows=members['members'];expected={r['file']:r for r in rows}
        if len(expected)!=len(rows) or len(rows)!=item['entries']:raise ValueError('Duplicate member index path or incorrect count')
        target=work/str(i);target.mkdir();names=[]
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None or z.namelist()!=sorted(expected):raise ValueError('Archive namespace/CRC differs')
            for info in z.infolist():
                member=info.filename;pure=PurePosixPath(member)
                if pure.is_absolute() or '..' in pure.parts or '\\' in member or ':' in member or (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe archive entry')
                body=z.read(info);row=expected[member]
                if sha(body)!=row['sha256'] or len(body)!=row['bytes']:raise ValueError('Member SHA/size differs: '+member)
                output=target.joinpath(*pure.parts);output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(body);names.append(member)
                text=body.decode('utf-8-sig');findings=private_findings(text)
                if findings:raise ValueError('Private archive content in '+member+': '+str(findings))
                if output.suffix=='.py':ast.parse(text,filename=member)
        links=check_links(target,names)
        if name.endswith('-native.zip'):
            if set(names)!=set(ADDON_FILES):raise ValueError('Native exact11 namespace mismatch')
            kind='native'
        elif '-skill-' in name:
            if [x for x in names if x.endswith('/SKILL.md')]!=['blender-compositing/SKILL.md']:raise ValueError('Standalone archive must have one skill')
            if any(n.startswith(('tools/','runtime/','models/')) for n in names):raise ValueError('Runtime payload in skill')
            kind='skill'
        elif name.endswith('-source.zip'):
            verify(target);kind='source'
        else:raise ValueError('Unknown archive role')
        if kind in trees:raise ValueError('Duplicate archive role')
        trees[kind]=target
        results.append({'archive':name,'kind':kind,'members':len(names),'local_links':links,'sha256':sha(data)})
    if set(trees)!={'native','skill','source'}:raise ValueError('Missing independent artifact role')
    source=trees['source']
    for member in ADDON_FILES:
        if (trees['native']/member).read_bytes()!=(source/'tools/compositing_workflow_addon'/member).read_bytes():raise ValueError('Native/source bytes differ: '+member)
    for p in (trees['skill']/'blender-compositing').rglob('*'):
        if p.is_file() and p.read_bytes()!=(source/'skills'/p.relative_to(trees['skill'])).read_bytes():raise ValueError('Skill/source bytes differ')
    return {'status':'passed_independent_archive_checks','artifacts':results,'skill_source_bytes_equal':True,'native_source_bytes_equal':True,'scope':'CPU parse, inventory, SHA/bytes, independent local links and targeted privacy; no runtime/visual certification'}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dist',type=Path,required=True);parser.add_argument('--work-dir',type=Path,required=True);args=parser.parse_args()
    try:print(json.dumps(verify_archives(args.dist,args.work_dir),indent=2))
    except (ValueError,OSError,KeyError,SyntaxError,TypeError,zipfile.BadZipFile) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);sys.exit(1)

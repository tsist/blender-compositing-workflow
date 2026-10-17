"""Build three deterministic source-only archives, refusing changed outputs."""
from __future__ import annotations
import argparse,importlib.util,io,json,sys,zipfile
from pathlib import Path
sys.dont_write_bytecode=True
from verify_release import ADDON,ADDON_FILES,ROOT,load_publication,release_files,safe_file,sha,verify
def archive(entries):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_STORED) as output:
        for name,data in sorted(entries):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.create_system=3
            info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_STORED;output.writestr(info,data)
    return buffer.getvalue()
def native_archive(root,entries):
    # Preserve the already qualified strict native builder's compression/metadata.
    spec=importlib.util.spec_from_file_location('strict_native_builder',root/'tools/blender/build_compositing_native.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    if tuple(module.MEMBERS)!=ADDON_FILES:raise ValueError('Strict native member contract differs')
    return module.archive_bytes(dict(entries))
def no_clobber(path,data):
    if path.is_symlink():raise ValueError('Refusing output symlink: '+path.name)
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('Refusing different existing output: '+path.name)
    else:
        with path.open('xb') as stream:stream.write(data)
def build(root=ROOT,dist=None):
    validation=verify(root);pub=load_publication(root);dist=dist or root/'dist'
    if dist.is_symlink():raise ValueError('Refusing symlink output directory')
    dist.mkdir(parents=True,exist_ok=True)
    names=release_files(pub);source=[(x,safe_file(root,x).read_bytes()) for x in names]
    native=[(x,safe_file(root,ADDON+x).read_bytes()) for x in ADDON_FILES]
    skill=[(x[len('skills/'):],data) for x,data in source if x.startswith('skills/')]
    skill.extend((x,safe_file(root,x).read_bytes()) for x in ('LICENSE','NOTICE.md'))
    bundles={
        f'compositing-workflow-{pub["addon"]}-native.zip':(native,native_archive),
        f'blender-compositing-skill-{pub["skill"]}.zip':(skill,None),
        f'blender-compositing-workflow-{pub["release"]}-source.zip':(source,None),
    }
    artifacts=[];planned=[]
    for name,(entries,encoder) in bundles.items():
        payload=encoder(root,entries) if encoder else archive(entries)
        repeat=encoder(root,entries) if encoder else archive(entries)
        if payload!=repeat:raise ValueError('Archive repeat bytes differ: '+name)
        if name.endswith('-native.zip') and sha(payload)!=pub['native_archive_sha256']:raise ValueError('Native compressed identity changed; requires separate archive acceptance')
        with zipfile.ZipFile(io.BytesIO(payload)) as check:
            if check.namelist()!=sorted(n for n,_ in entries) or check.testzip() is not None:raise ValueError('Archive inventory/CRC mismatch')
            for entry,data in entries:
                if check.read(entry)!=data:raise ValueError('Archive member bytes differ: '+entry)
        index={'schema':'compositing-release-member-index-v1','archive':name,'sha256':sha(payload),'bytes':len(payload),'members':[{'file':n,'sha256':sha(d),'bytes':len(d)} for n,d in sorted(entries)]}
        index_name=name.removesuffix('.zip')+'.members.json'
        planned.extend(((dist/name,payload),(dist/index_name,(json.dumps(index,ensure_ascii=False,indent=2)+'\n').encode())))
        artifacts.append({'file':name,'sha256':sha(payload),'bytes':len(payload),'entries':len(entries),'member_index':index_name})
    sums=''.join(x['sha256']+'  '+x['file']+'\n' for x in sorted(artifacts,key=lambda x:x['file']))
    planned.append((dist/'SHA256SUMS',sums.encode()))
    result={'status':'passed_deterministic_release_build','validation':validation,'artifacts':artifacts,'scope':'Source-only; runtime and visual acceptance separate'}
    planned.append((dist/'release-index.json',(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()))
    # Check every collision before writing any new member of a release batch.
    for path,data in planned:
        if path.is_symlink() or path.exists() and path.read_bytes()!=data:raise ValueError('Refusing different existing output: '+path.name)
    for path,data in planned:no_clobber(path,data)
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path);args=parser.parse_args()
    try:print(json.dumps(build(dist=args.output_dir),indent=2))
    except (ValueError,OSError,KeyError,SyntaxError,TypeError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);sys.exit(1)

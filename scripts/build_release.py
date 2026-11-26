"""Build three deterministic source-only archives, refusing changed outputs."""
from __future__ import annotations
import argparse,io,json,sys,zipfile
from pathlib import Path
sys.dont_write_bytecode=True
from verify_release import ADDON,NATIVE_FILES,ROOT,load_publication,release_files,safe_file,sha,verify
def archive(entries):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_STORED) as output:
        for name,data in sorted(entries):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.create_system=3
            info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_STORED;output.writestr(info,data)
    return buffer.getvalue()
def native_archive(entries,layout):
    contents=dict(entries)
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for row in layout:
            name=row['file']
            info=zipfile.ZipInfo(name,date_time=tuple(row['date_time']))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=row['create_system']
            info.external_attr=row['external_attr']
            output.writestr(info,contents[name],compresslevel=9)
    return buffer.getvalue()
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
    native=[(x,safe_file(root,ADDON+x).read_bytes()) for x in NATIVE_FILES]
    skill=[(x[len('skills/'):],data) for x,data in source if x.startswith('skills/')]
    skill.extend((x,safe_file(root,x).read_bytes()) for x in ('LICENSE','NOTICE.md'))
    bundles={
        f'compositing-workflow-{pub["addon"]}-native.zip':(native,pub['native_archive_layout']),
        f'blender-compositing-skill-{pub["skill"]}.zip':(skill,None),
        f'blender-compositing-workflow-{pub["release"]}-source.zip':(source,None),
    }
    artifacts=[];planned=[]
    for name,(entries,layout) in bundles.items():
        payload=native_archive(entries,layout) if layout else archive(entries)
        repeat=native_archive(entries,layout) if layout else archive(entries)
        if payload!=repeat:raise ValueError('Archive repeat bytes differ: '+name)
        if name.endswith('-native.zip') and sha(payload)!=pub['native_archive_sha256']:raise ValueError('Native compressed identity changed; requires separate archive acceptance')
        order=[row['file'] for row in layout] if layout else sorted(n for n,_ in entries)
        with zipfile.ZipFile(io.BytesIO(payload)) as check:
            if check.namelist()!=order or check.testzip() is not None:raise ValueError('Archive inventory/CRC mismatch')
            for entry,data in entries:
                if check.read(entry)!=data:raise ValueError('Archive member bytes differ: '+entry)
        contents=dict(entries)
        index={'schema':'compositing-release-member-index-v1','archive':name,'sha256':sha(payload),'bytes':len(payload),'members':[{'file':n,'sha256':sha(contents[n]),'bytes':len(contents[n])} for n in order]}
        index_name=name.removesuffix('.zip')+'.members.json'
        planned.extend(((dist/name,payload),(dist/index_name,(json.dumps(index,ensure_ascii=False,indent=2)+'\n').encode())))
        artifacts.append({'file':name,'sha256':sha(payload),'bytes':len(payload),'entries':len(entries),'member_index':index_name})
    license_text=safe_file(root,'LICENSE').read_bytes()
    license_asset={'file':'LICENSE','sha256':sha(license_text),'bytes':len(license_text)}
    planned.append((dist/'LICENSE',license_text))
    sums=''.join(x['sha256']+'  '+x['file']+'\n' for x in sorted([*artifacts,license_asset],key=lambda x:x['file']))
    planned.append((dist/'SHA256SUMS',sums.encode()))
    result={'status':'passed_deterministic_release_build','validation':validation,'artifacts':artifacts,'license':license_asset,'scope':'Source-only; runtime and visual acceptance separate'}
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

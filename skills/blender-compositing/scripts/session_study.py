"""Review candidate only. Finite stdlib orchestration of existing public APIs.

Not a public CLI operation; no model/GPU imports, launch bypass, or trust profile.
Real session/cancel/timeout acceptance is intentionally NOT claimed by this file.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,os,re,signal,subprocess,sys,time,traceback,uuid
from pathlib import Path

STOP=False
MAX_COMMANDS=10000
TERMINAL_STATES=frozenset(('succeeded','failed','cancelled','timed_out'))
# Compatibility rule for a public launch check that currently has no pure helper.
# An updated reviewed source index must NOT silently accept a changed runner rule.
RUNNER_COMPATIBILITY={
    'path':'tools/blenderctl/runner.py',
    'sha256':'7556f96b80d0597edc26a945a3ef19c738ff9f4bb832e49250191ec37e66ab13',
    'rule':'lifetime_seconds + relight.budget.timeout_seconds + 90',
    'runtime_cleanup_allowance_seconds':90,
}
PURE_MODULES=(
    'protocol','filesystem',
    'compositing_depth_contract','compositing_relight_kernel',
    'compositing_relight_local_edits','compositing_relight_contract',
    'compositing_relight_session_contract','compositing_relight_session_client',
)
def interrupted(*_):
    global STOP
    STOP=True
def need(value,message):
    if not value:raise ValueError(message)
def check_stop():
    if STOP:raise InterruptedError('Driver interrupted; no new submission authorized')
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def strict(raw):
    def pairs(rows):
        out={}
        for k,v in rows:
            need(k not in out,'Duplicate JSON key: '+k);out[k]=v
        return out
    return json.loads(raw.decode('utf-8-sig'),object_pairs_hook=pairs,
                      parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON '+x)))
def load(path):
    need(Path(path).stat().st_size<=16*1024*1024,'JSON exceeds16MiB')
    return strict(Path(path).read_bytes())
def encode(value):return json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2).encode('utf-8')
def exclusive(path,data):
    with Path(path).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def absolute(value):
    p=Path(value);need(p.is_absolute(),'Explicit absolute path required: '+value)
    need(not str(p).startswith(('\\\\?\\','\\\\.\\')),'No long-path/device namespace rewrite')
    return p.resolve()
def pinned(path,expected):
    need(re.fullmatch('[0-9a-f]{64}',expected) is not None,'Exact lowercase SHA256 required')
    need(Path(path).is_file() and digest(path)==expected,'Pinned file SHA differs: '+str(path))
def pinned_bytes(path,expected):
    """Bind parsing to the exact bounded bytes whose SHA was checked."""
    need(re.fullmatch('[0-9a-f]{64}',expected) is not None,'Exact lowercase SHA256 required')
    with Path(path).open('rb') as stream:raw=stream.read(16*1024*1024+1)
    need(len(raw)<=16*1024*1024,'JSON exceeds16MiB')
    need(hashlib.sha256(raw).hexdigest()==expected,'Pinned file SHA differs: '+str(path))
    return raw
def descriptor(path):
    p=Path(path);return {'file':str(p),'sha256':digest(p),'bytes':p.stat().st_size}
def source_files(root):
    return sorted(p for folder in ('tools/blenderctl','tools/compositing_workflow_addon')
                  for p in (root/folder).rglob('*.py') if '__pycache__' not in p.parts)
def verify_sources(root,index):
    need(type(index) is dict and set(index)=={'schema','files'} and index['schema']=='relight-helper-source-index-v1','Invalid source index')
    need(type(index['files']) is list and 1<=len(index['files'])<=2000,'Bounded source index required')
    rows={}
    for row in index['files']:
        need(type(row) is dict and set(row)=={'path','sha256'},'Source index row must be path/SHA')
        p=Path(row['path']);need(not p.is_absolute() and '..' not in p.parts,'Relative in-root source path required')
        target=(root/p).resolve();need(target.is_relative_to(root) and target.suffix=='.py','Source escaped root')
        need(target not in rows,'Duplicate source index path');pinned(target,row['sha256']);rows[target]=row['sha256']
    need(set(rows)==set(source_files(root)),'Source Python namespace differs from reviewed source index')
    return rows
def verified_modules(root,sources):
    """Load a fixed reviewed stdlib dependency closure from checked bytes, never stale pyc.

    A previously loaded module needs this loader's exact-source marker as well
    as spec/file/SHA agreement. Unknown cached provenance requires a fresh driver;
    no module is deleted or silently reloaded. This is provenance, not an OS sandbox.
    """
    folder=root/'tools/blenderctl'
    def check_cached(name,module):
        path=(folder/(name+'.py')).resolve()
        need(path in sources,'Reviewed module absent from source index: '+name)
        spec=getattr(module,'__spec__',None)
        need(spec is not None and spec.origin is not None and
             Path(spec.origin).resolve()==path and
             Path(getattr(module,'__file__','')).resolve()==path,
             'Conflicting loaded module origin: '+name)
        need(getattr(module,'_study_helper_source_sha256',None)==sources[path],
             'Unreviewed loaded module body; restart driver: '+name)
        pinned(path,sources[path])
    # Reject the entire cached conflict set before executing any new module.
    for name in PURE_MODULES:
        if name in sys.modules:check_cached(name,sys.modules[name])
    prior=list(sys.path)
    try:
        sys.path.insert(0,str(folder))
        for name in PURE_MODULES:
            if name not in sys.modules:
                path=(folder/(name+'.py')).resolve()
                need(path in sources,'Reviewed module absent from source index: '+name)
                raw=pinned_bytes(path,sources[path])
                spec=importlib.util.spec_from_file_location(name,path)
                need(spec is not None and spec.origin is not None and
                     Path(spec.origin).resolve()==path,'Unexpected exact-file module spec: '+name)
                module=importlib.util.module_from_spec(spec)
                # Dependencies are topologically loaded above. A failed import
                # remains visibly incomplete; a subsequent attempt cannot reuse it.
                sys.modules[name]=module
                exec(compile(raw,str(path),'exec'),module.__dict__)
                module._study_helper_source_sha256=sources[path]
            check_cached(name,sys.modules[name])
        bridge=sys.modules['compositing_depth_contract']
        dynamic=(root/'tools/compositing_workflow_addon/depth_contract.py').resolve()
        need(dynamic in sources,'Dynamic depth source absent from index')
        need(Path(bridge.CONTRACT_PATH).resolve()==dynamic and
             Path(bridge._module.__file__).resolve()==dynamic,
             'Dynamic depth bridge source origin differs')
        need(bridge._source_sha256==sources[dynamic] and
             hashlib.sha256(bridge._source_bytes).hexdigest()==sources[dynamic],
             'Dynamic depth bridge loaded source SHA differs')
        pinned(dynamic,sources[dynamic]);bridge._check_loaded_source()
        return {name:sys.modules[name] for name in PURE_MODULES}
    finally:sys.path[:]=prior

def output_file(out,family,*,number=0,revision=12,token=None):
    """One filename contract shared by every helper write and path projection."""
    token=uuid.uuid4().hex if token is None else token
    need(re.fullmatch('[0-9a-f]{32}',token) is not None,'Exact temp token required')
    fixed={'request':'FROZEN-REQUEST.json','actions':'FROZEN-ACTIONS.json',
           'source_index':'FROZEN-SOURCE-INDEX.json','preflight':'PREFLIGHT.json',
           'state':'STATE.json','index':'INDEX.json','summary':'SUMMARY.json','failure':'FAILURE.json'}
    if family in fixed:name=fixed[family]
    elif family=='state_temp':name='.state-'+token+'.tmp'
    elif family in ('stdout','stderr'):
        need(type(number) is int and 0<=number<MAX_COMMANDS,'Command evidence budget exhausted')
        name=f'command-{number:03d}'+('.stdout.json' if family=='stdout' else '.stderr.log')
    elif family=='revision':
        need(type(revision) is int and 1<=revision<=12,'Owned finite revision outside1..12')
        name=f'revision-{revision:09d}.json'
    else:raise ValueError('Unknown output filename family: '+family)
    return Path(out)/name

def path_budget(jobs,outdir):
    # UTF-16 units, conservative 239 policy; NOT generic Windows long-path support.
    j=jobs/('f'*32);rev='000000012-'+('f'*32);temp='.'+('f'*32)+'.json.partial'
    suffixes=[Path('session/gpu/revisions')/rev/temp,
       Path('session/gpu/depth/commands')/temp,
       Path('session/generations')/('f'*64)/'normal_validity.npy',
       Path('session/generations')/('f'*64)/'generation.json',
       Path('session/source')/('session-compositing_relight_session_owned_worker.py'),
       Path('session/pack/depth')/temp,Path(temp)]
    families=('request','actions','source_index','preflight','state','index','summary','failure','state_temp','stdout','stderr','revision')
    paths=[str(j/x) for x in suffixes]+[str(output_file(outdir,f,number=MAX_COMMANDS-1,token='f'*32)) for f in families]
    counts=[len(p.encode('utf-16-le'))//2 for p in paths]
    need(max(counts)<240,'Projected final/temp path exceeds conservative239 UTF16 policy; choose shorter NEW jobs/out roots')
    return {'policy':'conservative UTF16<240, current known publication families only','max_utf16_units':max(counts),'paths':paths}
def preflight(a):
    root=absolute(a.cli_root);python=absolute(a.bundled_python);req=absolute(a.request);act=absolute(a.actions)
    out=absolute(a.outdir);jobs=absolute(a.jobs_dir);indexpath=absolute(a.source_index)
    need(Path(sys.executable).resolve()==python,'Driver must itself be launched by explicit bundled Python; do not reexec from venv')
    pinned(python,a.python_sha256)
    need(python.parent.name=='bin' and python.parent.parent.name=='python','Expected installed Blender python/bin layout')
    need(sys.prefix==sys.base_prefix,'Venv driver rejected')
    ib=pinned_bytes(indexpath,a.source_index_sha256)
    index=strict(ib);sources=verify_sources(root,index)
    runner=(root/RUNNER_COMPATIBILITY['path']).resolve()
    need(sources.get(runner)==RUNNER_COMPATIBILITY['sha256'],
         'Public runner compatibility changed; review launch budget rule before using helper')
    for name in ('numpy','OpenImageIO'):
        spec=importlib.util.find_spec(name)
        need(spec is not None and spec.origin is not None,'Bundled numeric module not found: '+name)
        need(Path(spec.origin).resolve().is_relative_to(python.parent.parent),'Numeric origin outside explicit bundled Python: '+name)
    # Origins are a cheap stdlib diagnostic; public runtime_identity/guards still perform actual admission.
    rb=pinned_bytes(req,a.request_sha256);ab=pinned_bytes(act,a.actions_sha256)
    request=strict(rb);actions=strict(ab)
    need(type(request) is dict and set(request)=={'schema_version','command','params'} and request['schema_version']=='1.0' and request['command']=='compositing.depth-session','Only public depth-session request accepted')
    need(type(actions) is dict and set(actions)=={'actions','stop'} and actions['stop'] is True,'Canonical finite actions + mandatory stop:true required')
    need(type(actions['actions']) is list and 1<=len(actions['actions'])<=12,'Require1..12 actions')
    modules=verified_modules(root,sources)
    contract=modules['compositing_relight_session_contract']
    relight=modules['compositing_relight_contract']
    local_signature=modules['compositing_relight_local_edits'].signature
    p=contract.normalize_params(request['params'])
    bundle=strict(pinned_bytes(p['relight']['bundle']['file'],p['relight']['bundle']['expected_sha256']))
    domain=relight.admit_bundle(p['relight'],bundle)
    contract.preview_domain(domain,p['preview_divisor'])
    names=set();normalized=[];recipes=set()
    for action in actions['actions']:
        need(type(action) is dict and set(action)=={'name','kind','config','local_edits'},'Flat canonical name/kind/config/local_edits required')
        name=action['name'];need(type(name) is str and 0<len(name)<=64 and name not in names,'Unique bounded action name required');names.add(name)
        value=contract.normalized_parameters({k:action[k] for k in ('kind','config','local_edits')},p['relight']['config'])
        action_params=copy.deepcopy(p['relight']);action_params['config']=value['config']
        relight.admit_bundle(action_params,bundle)
        normalized.append({'name':name,**value})
        if value['local_edits']['regions']:recipes.add(local_signature(value['local_edits']))
    need(p['max_revisions']>=len(normalized),'Revision cap too small')
    need(len(recipes)<=p.get('max_data_generations',16),'Data generation cap too small')
    need(a.revision_seconds>=p['revision_timeout_seconds']+10,'Revision wait needs explicit Host publication margin')
    need(p['idle_seconds']>=a.revision_seconds+5,'Idle budget insufficient for one bounded revision')
    need(p['lifetime_seconds']>=len(normalized)*a.revision_seconds+10,'Lifetime insufficient for frozen finite actions')
    need(a.parent_timeout>=a.ready_seconds+len(normalized)*a.revision_seconds+a.close_seconds,'Parent timeout too small for explicit bounded phases')
    public_minimum=p['lifetime_seconds']+p['relight']['budget']['timeout_seconds']+RUNNER_COMPATIBILITY['runtime_cleanup_allowance_seconds']
    need(a.parent_timeout>=public_minimum,'Parent timeout below reviewed public runner launch minimum: '+str(public_minimum))
    finals=sum(x['kind']=='final' for x in normalized)
    need(finals>0 if a.intent=='requires_final' else finals==0,'Explicit study intent does not match final actions')
    resource_rows=[]
    for item in p['relight']['resources']:
        pinned(item['file'],item['expected_sha256']);resource_rows.append(descriptor(item['file']))
    # Do not expand/reinterpret private runtime profiles or16k payloads. Public admission remains authoritative.
    for path in (out,jobs):need(not path.exists(),'Fresh directory required (no silent resume/overwrite): '+str(path))
    need(out!=jobs and not out.is_relative_to(jobs) and not jobs.is_relative_to(out),'Independent sibling jobs/out directories required')
    budget=path_budget(jobs,out)
    return {'root':root,'python':python,'out':out,'jobs':jobs,'request':request,'raw_request':rb,'raw_actions':ab,
       'actions':normalized,'source_index':index,'raw_source_index':ib,'sources':sources,'resources':resource_rows,'path_budget':budget,
       'runner_compatibility':dict(RUNNER_COMPATIBILITY,minimum_parent_timeout=public_minimum),
       'numeric_origin_policy':'stdlib find_spec only; public actual runtime identity and guards unchanged'}

class Run:
    def __init__(self,a,p):
        self.a=a;self.p=p;self.job=None;self.client=None;self.records=[];self.commands=[];self.primary=None
        self.last_status_evidence=None
        self.read_status=verified_modules(p['root'],p['sources'])['filesystem'].read_shared_bytes
        self.out=p['out'];self.out.mkdir(parents=True,exist_ok=False)
        self.state={'schema':'relight-finite-study-state-v2','submit_attempted':False,'job_id':None,'records':[],
                    'cleanup_complete':False,'recovery_job_directory':None}
        exclusive(self.file('request'),p['raw_request'])
        exclusive(self.file('actions'),p['raw_actions'])
        exclusive(self.file('source_index'),p['raw_source_index'])
        exclusive(self.file('preflight'),encode({'status':'passed','request_sha256':a.request_sha256,'actions_sha256':a.actions_sha256,'actions':[x['name'] for x in p['actions']],'path_budget':p['path_budget'],'resources':p['resources'],'source_index_sha256':a.source_index_sha256,'preflight_only':a.preflight_only,'runner_compatibility':p['runner_compatibility']}))
        self.save()
    def file(self,family,**kwargs):return output_file(self.out,family,**kwargs)
    def verify_frozen(self):
        for family,expected,raw_key in (
                ('request',self.a.request_sha256,'raw_request'),
                ('actions',self.a.actions_sha256,'raw_actions'),
                ('source_index',self.a.source_index_sha256,'raw_source_index')):
            raw=pinned_bytes(self.file(family),expected)
            need(raw==self.p[raw_key],'Frozen bytes differ from admitted input: '+family)
            # Parsing is performed on these same SHA-bound bytes, never a second read.
            value=strict(raw)
            if family=='source_index':
                sources=verify_sources(self.p['root'],value)
                need(sources==self.p['sources'],'Reviewed source closure changed')
                verified_modules(self.p['root'],sources)
    def save(self):
        self.state.update(job_id=self.job.name if self.job else None,records=[{'name':r['name'],'revision':r['ticket']['revision']} for r in self.records])
        tmp=self.file('state_temp');exclusive(tmp,encode(self.state));os.replace(tmp,self.file('state'))
    def command(self,args,timeout=60):
        no=len(self.commands)
        cmd=[str(self.p['python']),'-B',str(self.p['root']/'tools/blenderctl/cli.py'),'--jobs-dir',str(self.p['jobs']),*args]
        row={'argv':cmd,'stdout':str(self.file('stdout',number=no)),'stderr':str(self.file('stderr',number=no))}
        self.commands.append(row)
        with Path(row['stdout']).open('xb') as out,Path(row['stderr']).open('xb') as err:
            r=subprocess.run(cmd,stdout=out,stderr=err,timeout=timeout,check=False)
        row['exit_code']=r.returncode
        return r.returncode,load(row['stdout'])
    def discover(self):
        if self.job:return
        candidates=[d for d in self.p['jobs'].iterdir() if d.is_dir() and re.fullmatch('[0-9a-f]{32}',d.name)]
        self.state['discovered_candidate_directories']=[str(d) for d in candidates]
        need(len(candidates)<=1,'Ambiguous owned fresh jobs directory; never resubmit')
        if candidates:
            req=load(candidates[0]/'request.json');need(req==self.p['request'],'Discovered request differs; do not claim foreign job: '+str(candidates[0]))
            self.job=candidates[0];self.state['recovery_job_directory']=str(self.job);self.save()
    def status(self):
        if not self.job:return None
        path=self.job/'status.json';raw=self.read_status(path)
        need(len(raw)<=16*1024*1024,'Status JSON exceeds16MiB')
        status=strict(raw)
        need(type(status) is dict and status.get('job_id')==self.job.name and
             status.get('state') in TERMINAL_STATES|{'queued','running'},'Invalid parent status authority')
        if status['state'] in TERMINAL_STATES:
            need(type(status.get('exit_code')) is int,'Terminal parent exit code missing')
        self.last_status_evidence={'file':str(path),'sha256':hashlib.sha256(raw).hexdigest(),
                                   'bytes':len(raw),'state':status['state'],'job_id':self.job.name}
        return status
    def bounded(self,fn,seconds):
        limit=time.monotonic()+seconds
        while time.monotonic()<limit:
            if STOP:raise InterruptedError('Driver interrupted')
            value=fn()
            if value:return value
            s=self.status()
            if s and s.get('state') not in ('queued','running'):raise RuntimeError('Parent became terminal before required publication')
            time.sleep(.1)
        raise TimeoutError('Bounded study phase expired')
    def terminal(self,seconds,allow_interrupt=True):
        until=time.monotonic()+seconds
        while time.monotonic()<until:
            if allow_interrupt and STOP:raise InterruptedError('Driver interrupted while awaiting parent terminal')
            s=self.status()
            if s and s['state'] not in ('queued','running'):return s
            self.command(['--compact','job','wait',self.job.name,'--wait-seconds',str(min(20,max(1,until-time.monotonic())))],timeout=60)
        return self.status()
    def cleanup(self):
        errors=[]
        self.state['cleanup_complete']=False
        try:self.discover()
        except Exception as e:errors.append({'discover':str(e)})
        if self.job:
            self.state['recovery_job_directory']=str(self.job)
            if self.client:
                try:self.client.stop()
                except Exception as e:errors.append({'stop':str(e)})
            try:
                s=self.status()
                if s['state'] in ('queued','running'):self.command(['--compact','job','cancel',self.job.name])
                terminal=self.terminal(self.a.close_seconds,allow_interrupt=False)
                self.state['parent_terminal_after_cleanup']=terminal
                self.state['cleanup_status_evidence']=self.last_status_evidence
                self.state['cleanup_complete']=bool(terminal and terminal['state'] in TERMINAL_STATES)
                if not self.state['cleanup_complete']:
                    errors.append({'terminal_not_confirmed':'Parent remains live or unknown; retained job requires recovery'})
            except Exception as e:errors.append({'cancel_or_wait':str(e)})
        elif self.state['submit_attempted']:
            errors.append({'ownership_not_confirmed':'Submission barrier crossed; never resubmit; inspect retained jobs directory'})
        self.state['cleanup_errors']=errors;self.save()
    def execute(self):
        check_stop()
        self.verify_frozen()
        check_stop()
        self.p['jobs'].mkdir(parents=True,exist_ok=False)
        # A final same-byte/SHA check precedes the irreversible submit barrier.
        self.verify_frozen()
        check_stop()
        self.state['submit_attempted']=True;self.save() # irreversible barrier: never retry submission after this point
        check_stop()
        code,response=self.command(['--timeout',str(self.a.parent_timeout),'--async','--compact','request',str(self.file('request'))])
        self.discover();need(code==0 and response.get('ok') is True and response.get('command')=='job.submit','Public submit failed')
        need(self.job is not None and response['job_id']==self.job.name,'Submit identity differs')
        modules=verified_modules(self.p['root'],self.p['sources'])
        SessionClient=modules['compositing_relight_session_client'].SessionClient
        self.bounded(lambda:(self.job/'session-ready.json').is_file(),self.a.ready_seconds)
        self.client=SessionClient(self.job/'session-ready.json')
        need(self.client.revision==0,'Fresh owned helper session already has revision messages')
        for action in self.p['actions']:
            check_stop()
            self.verify_frozen()
            check_stop()
            started=time.monotonic();ticket=self.client.submit(copy.deepcopy(action['config']),kind=action['kind'],reason=action['name'],local_edits=copy.deepcopy(action['local_edits']))
            manifest=self.bounded(self.client.poll,self.a.revision_seconds)
            record={'name':action['name'],'ticket':ticket,'manifest':manifest,'revision_wait_seconds':time.monotonic()-started};self.records.append(record)
            exclusive(self.file('revision',revision=ticket['revision']),encode(record));self.save()
        check_stop()
        self.client.stop();terminal=self.terminal(self.a.close_seconds);self.state['parent_terminal']=terminal;self.save()
        need(terminal and terminal['state']=='succeeded' and terminal['exit_code']==0,'Parent did not succeed; live publications remain non-deliverable')
        check_stop()
        _,result=self.command(['--compact','job','result',self.job.name])
        full=load(self.job/'result.json');report=load(self.job/'session-report.json');complete=load(self.job/'session-complete.json')
        need(full.get('ok') is True and report.get('status')=='closed' and complete.get('status')=='complete','Closed successful parent result required')
        need(len(report['verified_revisions'])==len(self.records),'Unexpected extra/missing publications in owned study')
        need({k:v for k,v in full['data'].items() if k!='complete'}==report,'Parent result and session report differ')
        actual=report['lifecycle']['actual_worker']
        need(actual.get('exit_confirmed') is True and actual.get('handle_closed') is True,'Actual worker exit/handle closure not confirmed')
        self.state['cleanup_complete']=True
        self.state['cleanup_status_evidence']=self.last_status_evidence
        self.save()
        d=complete['report'];need(Path(d['file']).resolve()==self.job/'session-report.json' and digest(d['file'])==d['sha256'] and Path(d['file']).stat().st_size==d['bytes'],'Complete report binding differs')
        need(complete['parent_job_id']==self.job.name and complete['last_passed']==report['last_passed'],'Closed parent identity differs')
        indexed=[]
        for row in self.records:
            m=row['manifest'];r=m['request'];folder=self.job/'session/gpu/revisions'/(str(r['revision']).zfill(9)+'-'+r['request_id'])
            receipt=load(folder/'host-verified.json')
            need(receipt.get('publication_decision')=='published' and {k:v for k,v in receipt.items() if k!='publication_decision'}==m,'Immutable receipt changed')
            need(m in report['verified_revisions'],'Closed report did not retain selected exact revision')
            refs=[]
            for member in m['members']:
                path=Path(member['file']).resolve();need(path.parent==folder,'Member escaped exact revision folder');pinned(path,member['sha256']);need(path.stat().st_size==member['bytes'],'Member byte length differs');refs.append(member)
            if m.get('generation'):
                g=m['generation'];gfolder=self.job/'session/generations'/m['derived_cache_id']
                need(Path(g['file']).resolve()==gfolder/'generation.json','Generation escaped exact derived namespace')
                pinned(g['file'],g['sha256']);need(Path(g['file']).stat().st_size==g['bytes'],'Generation bytes differ')
                generation=load(g['file'])
                for member in generation['members']:
                    need(Path(member['file']).resolve().parent==gfolder,'Generation member escaped namespace')
                    pinned(member['file'],member['sha256']);need(Path(member['file']).stat().st_size==member['bytes'],'Generation member bytes differ')
            indexed.append({'name':row['name'],'kind':r['parameters']['kind'],'revision':r['revision'],'request_id':r['request_id'],'parameters_sha256':r['parameters_sha256'],'host_receipt':descriptor(folder/'host-verified.json'),'members':refs,'generation':m.get('generation')})
        self.verify_frozen()
        check_stop()
        return {'schema':'relight-finite-study-index-v2','status':'passed','authority':'successful public parent + exact immutable publications; not image/aesthetic acceptance','job_id':self.job.name,'job_directory':str(self.job),'intent':self.a.intent,'parent_status':descriptor(self.job/'status.json'),'parent_result':descriptor(self.job/'result.json'),'session_complete':descriptor(self.job/'session-complete.json'),'session_report':descriptor(self.job/'session-report.json'),'request':descriptor(self.file('request')),'actions':descriptor(self.file('actions')),'source_index':descriptor(self.file('source_index')),'source_index_sha256':self.a.source_index_sha256,'runner_compatibility':self.p['runner_compatibility'],'revisions':indexed,'commands':self.commands}

def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('cli-root','bundled-python','python-sha256','source-index','source-index-sha256','request','request-sha256','actions','actions-sha256','jobs-dir','outdir'):p.add_argument('--'+name,required=True)
    p.add_argument('--intent',required=True,choices=('previews_only','requires_final'))
    p.add_argument('--ready-seconds',type=int,default=180);p.add_argument('--revision-seconds',type=int,default=130)
    p.add_argument('--close-seconds',type=int,default=240);p.add_argument('--parent-timeout',type=int,default=2200)
    p.add_argument('--preflight-only',action='store_true');return p
def main(argv=None):
    a=parser().parse_args(argv);run=None;start=time.monotonic()
    try:
        for name in ('ready_seconds','revision_seconds','close_seconds','parent_timeout'):
            need(1<=getattr(a,name)<=3600,'Bounded positive budgets required')
        p=preflight(a);run=Run(a,p)
        if a.preflight_only:
            print(json.dumps({'status':'preflight_passed','submitted':False,'preflight':str(run.file('preflight'))}));return 0
        for sig in ('SIGINT','SIGTERM','SIGBREAK'):
            if hasattr(signal,sig):signal.signal(getattr(signal,sig),interrupted)
        index=run.execute()
        run.verify_frozen();check_stop()
        exclusive(run.file('index'),encode(index))
        summary={'status':'passed','job_id':run.job.name,'revision_count':len(run.records),
                 'index':descriptor(run.file('index')),'wall_seconds':time.monotonic()-start}
        check_stop()
        exclusive(run.file('summary'),encode(summary));print(json.dumps(summary));return 0
    except BaseException as exc:
        failure={'status':'failed','error':{'type':type(exc).__name__,'message':str(exc)},'parent_authority_not_overridden':True,'traceback':traceback.format_exc(),'wall_seconds':time.monotonic()-start}
        if run:
            run.primary=failure
            if run.state['submit_attempted']:
                try:run.cleanup()
                except BaseException as secondary:
                    failure['secondary_cleanup_persistence_error']={'type':type(secondary).__name__,'message':str(secondary)}
            failure.update(job_id=run.job.name if run.job else None,records=run.records,commands=run.commands,cleanup=run.state)
            try:exclusive(run.file('failure'),encode(failure))
            except BaseException as secondary:
                failure['secondary_failure_persistence_error']={'type':type(secondary).__name__,'message':str(secondary)}
        print(json.dumps({'status':'failed','message':str(exc),'job_id':run.job.name if run and run.job else None,
                          'failure':str(run.file('failure')) if run else None,'resubmit':False,
                          'cleanup_complete':run.state['cleanup_complete'] if run else False,
                          'secondary_cleanup_error':failure.get('secondary_cleanup_persistence_error'),
                          'secondary_failure_error':failure.get('secondary_failure_persistence_error')}));return 1
if __name__=='__main__':raise SystemExit(main())

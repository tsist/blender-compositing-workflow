# Compositing Workflow

Experimental prerelease **0.8.0**: the two named native1080p/24fps/full120 stable relight shots and user continuous viewing passed. Strong full120 lighting experiments were artistically rejected; use the stable versions. Exact scope, retained failures and unverified limits are recorded below.


[简体中文](README.zh-CN.md)

Experimental editable compositor workflows and depth-based relighting for Blender. Add-on **0.8.0**, compatible CLI source **0.75.0**, portable skill **0.8.0**; GPL-3.0-or-later. The local baseline is Windows, Blender 5.2.1 LTS / build `9e2066aef7ef`.

Use managed native node graphs, explicit image/Render Layers bindings, bounded sequences and SDR Movie inputs, templates, batches, finite candidates, protected saved candidates and technical HDR encoding. Depth tools prepare or inspect data, estimate relative depth in a fixed approved GPU environment, relight a successful bundle, maintain a guarded live session, and process a declared 2–120-frame shot. These remain experimental; see [validation](docs/validation.md).

The native extension includes a **Relight** sidebar and source-root preferences. It is a GUI client of an already running external session. It does not install compute dependencies or start the model. Configure a matching source root, create a public session externally, then setup/bind its actual live ready record. Reopening a saved project requires a new session and explicit rebind. See [session usage](docs/relight-session.md).

Three separate source-only archives are built: native extension (exactly 11 members), one portable `blender-compositing` skill, and this compatible source tree. Install the native archive through Blender Preferences → Extensions → Install from Disk. Install the skill separately; its references and helper scripts are self-contained. No model, runtime binary, venv or production asset is bundled.

```powershell
$env:BLENDERCTL_ROOT = (Get-Location).Path
$env:BLENDERCTL_PYTHON = '<absolute-approved-Blender-bundled-python.exe>'
$env:BLENDER_PATH = '<absolute-blender.exe>'
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --version
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe --operation depth-sequence --schema
```

The 13 public operations are `compositing.run`, `compositing.inspect`, `compositing.encode`, `compositing.template-save`, `compositing.template-run`, `compositing.batch`, `compositing.study`, `compositing.depth-prepare`, `compositing.depth-inspect`, `compositing.depth-estimate`, `compositing.depth-relight`, `compositing.depth-session`, `compositing.depth-sequence`. A launcher Python version check is only syntax eligibility. Host bundled Python, the fixed GPU native environment and Blender GUI have different roles; see [dependencies](docs/dependencies.md) before submission. The fixed GPU profile is not distributed or portable to a new machine. No sanitized replacement profile or automatic installer is supplied.

The exact runtime namespace contains **213 files**, aggregate `ae89b1e85145c2d2385bc7db312557aee9e44499108299dc18dac7b48cd34370`. Separate source/profile identities, including the sequence producer subset, are not interchangeable. The original Geometry Nodes support import remains separately inventoried (7 Python sources + manifest); no second GUI extension activation is required. Other bundled domain sources do not certify those workflows.

Read [usage](docs/usage.md), [contract](docs/contract.md), [skill installation](docs/SKILLS.md), [license scope](docs/licensing.md) and [third-party notice](NOTICE.md). Depth Anything V2 source is Apache-2.0; the fixed Large weights are CC-BY-NC-4.0 and are external. GPL code does not grant commercial weight rights.

`python scripts/verify_release.py` checks source inventories, versions, syntax, local links and targeted privacy. `python scripts/build_release.py` produces deterministic archives with member indexes; `python scripts/verify_archives.py --dist dist --work-dir '<new-unpack-directory>'` independently extracts and checks all three. These CPU checks do not certify runtime or visual quality. Named full120 stable motion, final exported helper and real GUI chains passed within the explicit validation limits; strong experiments and extra AI-review failures remain recorded.

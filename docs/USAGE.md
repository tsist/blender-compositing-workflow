# Public CLI usage

Use this checkout's `blenderctl.ps1` and matching addon/CLI snapshot. Set `BLENDERCTL_ROOT` to its actual root. The launcher needs an explicit `BLENDERCTL_PYTHON` or a suitable Python 3.12+ on PATH; pass `--blender` to use the actual Blender 5.2.1 executable. Dependencies and tested versions are listed in `docs/DEPENDENCIES.md`.

## Discover contracts

```powershell
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --version
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe --operation run --schema
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe --section components
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe --section source
```

`describe` does not launch Blender or create a job. Seven public operations are run, inspect, encode, template-save, template-run, batch and study. create/update/adopt/detach remain `manifest.operation` actions within run. Read the selected operation's live schema; file existence and JSON Schema do not replace semantic preflight or actual node/RNA/image validation.

## Submit and retrieve

Requests are UTF-8 JSON with `schema_version`, `command`, and `params`. Supply actual absolute source/resource paths, expected SHA-256, explicit context, one manifest and applicable preview configuration. Source is a saved disk snapshot; GUI unsaved changes are not observed. Save a new independent snapshot before handing manual edits back to CLI.

```powershell
$compositingJobs = Join-Path $env:BLENDERCTL_ROOT 'runtime/compositing-jobs'
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --blender $env:BLENDER_PATH --jobs-dir $compositingJobs --timeout 1800 --async --compact request '<absolute-request.json>'
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --jobs-dir $compositingJobs --compact job wait '<job_id>' --wait-seconds 30
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --jobs-dir $compositingJobs --compact job result '<job_id>'
```

Global options precede subcommands. Keep the same explicit jobs directory across submission/wait/status/result/cancel, and keep the original job ID if wait still reports running. A queued/running or checkpoint report is not the supervisor's terminal success. Check CLI exit code, `ok/error`, final state, full report, source/resource/candidate/output hashes and independent image decoding. Compact only summarizes the bounded result.

## Inputs and output

Render Layers bind an explicit Scene/View Layer and actual pass set. Image/EXR inputs require explicit colorspace and alpha mode; multilayer inputs require the actual layer. Preview dimensions define the output canvas, not automatic fit. Match input dimensions or author an explicit Scale/Transform to avoid unintended center crop. Compare the original image as well as baseline/result.

Already display-encoded sRGB PNG can be mapped again if the source scene uses AgX. When the target is retaining that existing appearance, prepare an independent Standard/sRGB source with None look, view exposure 0 and gamma 1; do not overwrite the original or global preferences. See `docs/COLOR-HDR.md`. EXR values and their color/Alpha identity remain separately verified.

`engine=SOURCE` retains the source engine; it does not mean `device=SOURCE`. Declare the desired device behavior and report requested/used/fallback. Selected GPU is not proof of GPU kernel utilization or OIDN backend. Preview configuration is temporary; the saved candidate can retain the original source resolution/settings. For manual final rendering, set the intended dimensions and quality explicitly.

## Templates, batches and candidates

template-save consumes a complete passed producer report and explicit slots. template-run binds new source/input files, SHA, context and preview. A saved template alone does not validate its next consumer. Resume uses the old **outer template-run report**, not a native report substituted as outer authority.

Batch stops affected items and continues independent items; partial success is not all-passed. Study produces finite static candidates from explicit declared parameters. Contact JPEGs show RGB; PNG/EXR support Alpha checks. Users choose among visual candidates; data means are not an artistic ranking.

Cancellation targets the task-owned job through the public CLI and requires the supervisor terminal state. Recovery creates a new attempt with original request/runtime/resource identities and a complete successful ancestor closure. Pending or unrestored frames are redone. Never rewrite old expected hashes or claim arbitrary mid-render resumption.

## Synthetic example

The source-only example creates its own 128×128 linear RGBA source/EXR, then builds an explicit +0.5 EV static request under the chosen local output directory. No production asset or original acceptance `.blend` is embedded. Run from this checkout with an unused fixture directory:

```powershell
& $env:BLENDER_PATH --background --factory-startup --disable-autoexec --python (Join-Path $env:BLENDERCTL_ROOT 'examples/create_fixture.py') -- --output '<new-absolute-fixture-directory>'
& $env:BLENDERCTL_PYTHON (Join-Path $env:BLENDERCTL_ROOT 'examples/make_request.py') --fixture '<fixture-directory>/fixture.json' --output '<new-absolute-request.json>'
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --blender $env:BLENDER_PATH --jobs-dir '<absolute-example-jobs>' --transactions-dir '<absolute-example-transactions>' --timeout 240 --compact request '<absolute-request.json>'
```

Inspect the generated request and exact local resource paths/SHAs. Use the returned editable candidate and live inspect schema to build an independent inspect request. `docs/VALIDATION.md` records final clean-checkout execution and decoding; script presence alone is not an execution claim.

For final delivery provide the editable candidate, actual before/after images, required EXR/video, full report and resource/recovery references. Record technical status, AI visual observation, user acceptance and HDR-device viewing separately.

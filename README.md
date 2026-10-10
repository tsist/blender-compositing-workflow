# Compositing Workflow

[简体中文](README.zh-CN.md)

An experimental Blender extension and companion agent skill for editable compositor graphs, protected saved-file work, actual image output and recoverable CLI jobs.

**Addon 0.4.0 · compatible blenderctl snapshot 0.63.0 · GPL-3.0-or-later.** Bounded local validation used Windows and Blender **5.2.1 LTS / build 9e2066aef7ef**. Other Blender versions and platforms require separate validation.

## Capabilities

- Managed native compositor groups, explicit create/update/adopt/detach, preserved external nodes and manual-edit conflict reporting.
- Image/EXR and Render Layers bindings, component recipes and extensible node graphs, explicit color/Alpha/resource identities.
- Bounded image sequences, numeric parameter animation, external BoxMask tracking data and strictly declared SDR Movie input.
- Saved recipes/templates, new-input consumers, bounded sequential batches, finite static study candidates and hash-bound recovery after cancellation or timeout.
- Editable `.blend` candidates, before/after PNG and linear EXR, explicit SDR video preview and technical HDR10/PQ encoding.

The extension contains native graph code and contracts. Its registration does not add a dedicated panel or operator; the compatible CLI drives complete execution, file protection, rendering and validation. Blender's native node editor provides manual editing. Movie decoding and HDR encoding require separately supplied runtimes. See [usage](docs/USAGE.md) and [dependencies](docs/DEPENDENCIES.md).

## Install and run

Install the extension ZIP from the matching release using Blender **Preferences → Extensions → Install from Disk**. Use this checkout's compatible CLI snapshot for automated work. No Blender, Python, codec or third-party Python package is bundled.

```powershell
$env:BLENDERCTL_ROOT = (Get-Location).Path
$env:BLENDERCTL_PYTHON = '<absolute-path-to-python.exe>'
$env:BLENDER_PATH = '<absolute-path-to-blender.exe>'
./blenderctl.ps1 --version
./blenderctl.ps1 compositing describe
./blenderctl.ps1 compositing describe --operation run --schema
./blenderctl.ps1 --blender $env:BLENDER_PATH --jobs-dir (Join-Path $env:BLENDERCTL_ROOT 'runtime/compositing-jobs') --timeout 1800 --async --compact request '<absolute-path-to-request.json>'
```

All global options precede subcommands. Requests bind actual absolute source/resource paths and SHA-256 hashes. Use the same explicit jobs directory for submission, status, result, wait and cancellation. Validate supervisor terminal state and the full hashed report; compact output is a summary.

The seven public operations are `compositing.run`, `compositing.inspect`, `compositing.encode`, `compositing.template-save`, `compositing.template-run`, `compositing.batch` and `compositing.study`. Discover fields with live `compositing describe`. See [skill installation](docs/SKILLS.md), [contract](docs/CONTRACT.md) and [validation](docs/VALIDATION.md).

## Scope and evidence

The compatible checkout retains all **177 compositing-identity runtime files** byte-for-byte, with implementation identity `9566cec1c2a9bf6db34c3085d964806b8ce7bafed1e0ae145bbb5259d655e629`. It also includes the byte-exact Geometry Nodes Workflow source support package (7 Python files + manifest), separately inventoried: compositing run imports its saved-candidate persistence helper through the compatible CLI. This source import requires no second GUI-addon activation. Packaging supporting/other domain modules does not certify complete geometry-domain or other workflows. This release does not refactor the runtime or introduce a submodule.

Local representative evidence covers 2K/4K static outputs, Cycles/Eevee sources, external image blending, a new sRGB held-out input, bounded temporal fixtures, templates, batches, study and cancellation/timeout recovery. Individual M1–M4 evidence retains its original implementation identity. Current package validation and public example execution are reported separately in [validation](docs/VALIDATION.md).

HDR bitstream/color/metadata checks, real mastering, HDR-device viewing, AI visual observation and user artistic acceptance have separate statuses. File existence, extension registration and successful schema checks do not prove a finished visual work or complete HDR certification.

This source repository excludes production assets, original acceptance images, private `.blend` files, full local audit jobs, private Wiki, working-memory records, credentials and external runtimes. It includes public summaries and independently installable skill references; see [license scope](docs/LICENSING.md).

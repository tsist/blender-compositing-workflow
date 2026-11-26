# Scene Compositor & Effects in Blender 5.3

Compositing Workflow 0.10.0 edits the native scene effect stack in Blender 5.3.0. The Windows build used for acceptance was `02f0899d78e3`. Use the separate [blenderctl v0.64.0 distribution](https://github.com/tsist/blenderctl/releases/tag/v0.64.0) with production release `1.0.0` for these operations.

From the blenderctl distribution, set the source path, exact scene and view layer, and actual Blender executable. The following example adds the Essentials Bloom effect to a saved copy-workflow input. Run the same request with `request = @{ operation = 'inspect' }` to read the stack and stable socket identifiers before editing an existing effect.

```powershell
$source = (Resolve-Path -LiteralPath './shot.blend').Path
$request = @{
  schema_version = '1.0'
  command = 'production.run'
  params = @{
    file = $source
    expected_sha256 = (Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant()
    release = '1.0.0'
    domain = 'compositing'
    context = @{ scene = 'Scene'; view_layer = 'ViewLayer' }
    request = @{
      operation = 'add'
      name = 'Shot Glow'
      source = @{ kind = 'ESSENTIALS'; name = 'Bloom' }
      preview = $true
      render = $true
    }
  }
}
$request | ConvertTo-Json -Depth 10 | Set-Content './scene-effect.json' -Encoding utf8
./blenderctl.ps1 --blender '<absolute-path-to-blender.exe>' request './scene-effect.json'
```

- Use `add` with source kind `LOCAL` for a compatible in-file compositor node group. For `add` or `move`, choose at most one of `index`, `before`, or `after`. Names identify effect instances.
- Use `update` with `parameters` keyed by socket identifier. Set `preview` and `render` independently. `bypass` disables both and preserves the instance for later use. `remove` checks for animation and driver dependencies before changing the stack.
- Use `create_group` with a named sequence of native compositor stages and optional exposed `controls`. The saved group can serve multiple instances, each with its own parameter values.
- Read `production-report.json` for before and after values, reopen status, and the candidate file and SHA-256. Follow-up requests can use that candidate as their input. Source bytes are protected. Confirm the final image at the actual camera, frame, and effect participation settings.

The new operations cover the scene compositor. VSE strip effects and GPU or cross-platform visual approval have separate workflows. Existing managed relighting retains its documented dependencies.

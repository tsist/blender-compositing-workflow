# Skill installation and maintenance

`skills/blender-compositing` is the public export of the existing compositing skill. It preserves the original compositing methods, guard rules and version boundaries; changes adapt checkout discovery, private evidence navigation and release status. It does not replace the project's local maintenance source or the existing personal installed entry.

Choose an explicit host skill directory. For Codex this is normally `skills` under its configured home; other agents use their own convention. Installation copies the skill and its public reference files, not Blender, CLI runtime, a memory plugin or account configuration.

```powershell
$compositingSkillSource = Join-Path $env:BLENDERCTL_ROOT 'skills/blender-compositing'
$compositingSkillDestination = Join-Path '<absolute-host-skill-root>' 'blender-compositing'
if (Test-Path -LiteralPath $compositingSkillDestination) { throw 'Skill already exists; compare and migrate explicitly.' }
Copy-Item -LiteralPath $compositingSkillSource -Destination $compositingSkillDestination -Recurse
```

Set `BLENDERCTL_ROOT` to this compatible checkout's absolute root, `BLENDERCTL_PYTHON` to the actual launcher Python, and pass the actual Blender binary via global `--blender`. Calling another checkout's launcher can select a different runtime identity. Host catalogs normally discover installation on the next turn or refresh; no claim is made that this current turn's catalog changes automatically.

The installed skill has standalone public references for contract, usage, validation, dependencies and HDR/color, so it does not require the original private Wiki. Hosts may use their existing `blender-cli` skill and persistent knowledge where available. Installation does not create a knowledge vault or enable maintenance automation.

Public documents under `docs/` are the maintained public sources. The corresponding `skills/blender-compositing/references/` files are byte-identical exported copies, recorded by the release inventory. Update the public sources and regenerate the matching references together; avoid independent edits to both copies. The local production maintenance skill remains the upstream instruction source for the next export.

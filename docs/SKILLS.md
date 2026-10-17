# One portable compositing skill

Install only the `blender-compositing` folder from the skill archive into your agent skill directory. It contains one SKILL.md, public references and two helpers. The source archive contains the same bytes. Native ZIP contains no skill. The source archive is the separate matching CLI dependency; set BLENDERCTL_ROOT to its absolute extracted root.

No author-local Wiki, memory plugin, other skill or personal path is required. Public docs are the maintained source and skill references are exact byte copies. The skill archive contains its own complete LICENSE and NOTICE. A portable skill does not make the fixed GPU runtime/profile portable.

Use [usage](usage.md), [dependencies](dependencies.md), [contract](contract.md) and the selected depth references. `scripts/alpha_layout.py` needs an explicit `--project-root` for independent skill installation; it only measures a guarded square opaque-core RGBA cutout, preserving pixels. `scripts/session_study.py` uses a reviewed source index, explicit bundled interpreter SHA and frozen request/actions to perform finite public session actions; see [finite study](finite-relight-study.md). A helper is not a new public operation or automatic visual winner.

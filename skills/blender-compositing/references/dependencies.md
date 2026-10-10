# Dependencies

This experimental release was locally validated on Windows with Blender **5.2.1 LTS / build 9e2066aef7ef**. The addon core checks the exact Blender version. Manifest minimum version is not proof that newer versions work. Linux/macOS and other runtimes are unverified.

| Facility | External requirements | Local observed version |
|---|---|---|
| CLI launcher | Python 3.12+; pass actual Blender executable | Python 3.13.13 in the tested Blender environment |
| Native graph execution | Blender/bpy, matching addon and actual saved source | Blender 5.2.1 / addon 0.4.0 |
| Saved-candidate persistence during run | Included byte-exact `tools/geometry_nodes_workflow_addon` support package | 7 Python files + manifest; separately inventoried support identity |
| Image validation/fresh read | NumPy, OpenImageIO, PyOpenColorIO, actual OCIO config/LUT files | Final release probe: NumPy 2.3.4; OIIO 3.1.13.1; OCIO 2.5.0 |
| SDR Movie/preview | Explicit ffmpeg and ffprobe files with hashes; required Python readers | Request-bound external executables |
| HDR10/PQ encode | Explicit Python/module/native-file closure, ffmpeg/ffprobe, OCIO config/LUT identity | CPU OCIO/NumPy and CPU libx265 Main10 route |

The final release probe used the explicitly selected Blender Python 3.13.13 and observed NumPy 2.3.4, OIIO 3.1.13.1 and OCIO 2.5.0. The earlier M5 package probe observed NumPy 2.4.1 from a user-site package; that historical source/version is not the current required environment. Both are recorded under their own evidence identities. Availability in this configured environment does not establish that every standard Blender download supplies all modules. This repository embeds no external module implementation, binary or OCIO runtime. Supply dependencies in the environment used by each actual worker/reader and verify them before running; the skill and launcher do not silently install packages.

Set `BLENDERCTL_PYTHON` to the host CLI Python. Pass global `--blender` explicitly to select the actual Blender executable. Setting the launcher Python alone does not install modules into Blender's worker environment. Preserve the original `tools/` directory layout; graph/core and fresh-reader imports use it.

The run path imports `geometry_workflow._retain_unlinked_ids` for candidate persistence. That module imports the Geometry Nodes Workflow core, inspection and contract package at load time. Accordingly this checkout includes its original support package under `tools/geometry_nodes_workflow_addon` (7 `.py` files and manifest). This is a required source import dependency of compositing run; it does not require enabling a second GUI addon. Its files are inventoried separately and do not enter the 177-file compositing implementation aggregate. Including them preserves the current architecture and does not certify complete geometry-domain behavior.

Final staging exposed this dependency through an actual `compositing.run` failure (`ModuleNotFoundError: geometry_nodes_workflow_addon`). The earlier M5 source archive had a successful inspect smoke, which does not prove an independent run closure. Final run validation must use the corrected public checkout and retain the original failure separately.

Request-specific media/encoding executables and native files use actual absolute paths and SHA-256 values. HDR runtime closure must match actual loaded module files. Do not transfer old machine paths/hashes into a new environment or modify old report hashes to claim a new validation.

Optional CLI domains retain separate addon/runtime requirements. Their source modules are present to preserve the compatible implementation identity; their end-to-end operation is outside this release's acceptance.

# Runtime dependencies and roles

The tested local baseline is Windows, Blender5.2.1 LTS/build9e2066aef7ef, add-on0.8.0 and CLI0.75.0. Manifest minimum version does not prove compatibility with another Blender.

| Role | Requirements and admission | Scope |
|---|---|---|
| Host orchestration/numeric IO | Set BLENDERCTL_PYTHON to the approved Blender bundled Python directly; actual NumPy/OpenImageIO/PyOpenColorIO and loaded native file closure are checked | Historical selected Host Python3.13.13, NumPy2.3.4/OIIO3.1.13.1/OCIO2.5.0; a PATH/venv Python syntax pass is insufficient |
| Fixed model/GPU native worker | Existing approved Python3.13.14 native image, 14 pinned packages/16221payloads, source/weight/profile and SHA guards; CUDA0 FP32 | No automatic installation, model/precision/device fallback, cross-machine profile migration or sanitized profile supplied |
| Blender worker and GUI | Explicit actual Blender executable, matching source tree, protected saved snapshot; GUI extension is a client of an externally started live session | GUI registration is separate from compute, binding, image acceptance and user interaction |
| Media/HDR | Explicit SHA-bound ffmpeg/ffprobe and required native/OCIO runtime closure | CPU OCIO/NumPy plus libx265 Main10 technical route; external codecs and binaries are not bundled |
| Candidate persistence | Included original geometry support package:7Python+manifest | Required import, separately inventoried; does not require another GUI addon activation or certify geometry workflows |

Host orchestration should run from bundled Python directly. A Store-backed material-processing venv may introduce user-site numeric modules even when it launches the same CLI executable, and the runtime guard should reject that environment. Keep material conversion in its separate process. Do not change the profile or trust a freshly observed manifest merely to bypass admission.

The optional model environment contains these externally installed packages:

| Package | Fixed observed version |
|---|---|
| filelock | 3.32.0 |
| fsspec | 2026.7.0 |
| Jinja2 | 3.1.6 |
| MarkupSafe | 3.0.3 |
| mpmath | 1.3.0 |
| NetworkX | 3.6.1 |
| NumPy | 2.4.6 |
| opencv-python-headless | 5.0.0.93 |
| Pillow | 12.3.0 |
| setuptools | 83.0.0 |
| SymPy | 1.14.0 |
| torch | 2.13.0+cu130 |
| torchvision | 0.28.0+cu130 |
| typing-extensions | 4.16.0 |

Their161installed LICENSE/NOTICE files were located and hashed for the configured environment. None of these package implementations, model checkout, weights, venv, wheel or binary payloads is redistributed. Their bundled third-party notices cannot be replaced by one top-level license label. See [licensing](licensing.md).

Selecting BLENDERCTL_ROOT changes source lookup, not runtime admission. The raw approved profile/manifest/receipts contain machine-specific data and are excluded. This source distribution offers no qualified setup for a new GPU machine. Inspect the real environment and preserve refusal diagnostics; do not invent a public profile. Request executable/module/resource paths and SHA values must describe the actual environment.

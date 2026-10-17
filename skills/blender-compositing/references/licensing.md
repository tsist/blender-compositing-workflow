# License and distribution scope

The Compositing Workflow add-on, compatible project CLI source snapshot,
schemas, exported compositing skill, public documentation and release tooling
are distributed under **GPL-3.0-or-later**. See the complete `LICENSE` supplied
with the relevant archive. Included project support sources retain their
existing license declarations and notices.

This release is **source-only**. It does not bundle model weights, the external
Depth Anything V2 source checkout, Python/Blender distributions, virtual
environments, wheels, CUDA libraries, third-party Python package payloads,
codecs, or production images, videos, textures or `.blend` assets. Dependencies
installed in a validation environment are separate from files distributed in
these archives. Importing an external package does not relicense that package.

## Depth Anything V2 source and Large weights are separate

The external Depth Anything V2 source LICENSE at commit
`a561b849ebae10a6f5ef49e26c83cbbcd36c71bf` is **Apache-2.0**:

[Official source LICENSE](https://github.com/DepthAnything/Depth-Anything-V2/blob/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf/LICENSE)

The **Depth-Anything-V2-Large weights** are identified separately. The official
Hugging Face model card at revision
`cbbb86a30ce19b5684b7a05155dc7e6cbc7685b9` declares **CC-BY-NC-4.0**:

[Exact-revision official model card](https://huggingface.co/depth-anything/Depth-Anything-V2-Large/blob/cbbb86a30ce19b5684b7a05155dc7e6cbc7685b9/README.md)

[Creative Commons Attribution-NonCommercial 4.0 International legal code](https://creativecommons.org/licenses/by-nc/4.0/legalcode.en)

The validated Large-model workflow in this project is intended for personal,
noncommercial experimentation. The CC license grants its covered rights for
noncommercial purposes subject to its conditions; it does not supply a
commercial license. "Noncommercial" is defined by the legal code in terms of
commercial advantage or monetary compensation, rather than simply whether
the user is an individual or an organization. Follow applicable attribution,
license-link and modification-notice conditions. A separate permission from
the relevant rights holder would be needed for uses not covered by the license.

The GPL license of this project's code and the Apache license of the external
model source **do not grant commercial rights to the Large weights**. The
project's GPL source license is not changed into a noncommercial license by
this dependency notice. This notice makes no blanket licensing determination
for every possible input, generated output, dataset or downstream use.

The fixed model profile remains an execution admission boundary. Selecting a
different source directory, changing a filename or substituting another model
does not establish license compatibility or runtime qualification.

## External runtime dependencies

The validated GPU environment used separately installed filelock, fsspec,
Jinja2, MarkupSafe, mpmath, NetworkX, NumPy, opencv-python-headless, Pillow,
setuptools, SymPy, PyTorch, torchvision and typing-extensions. Their package
payloads and their bundled third-party components are **not included** in this
source-only release. Their actual installed LICENSE/NOTICE files remain the
authority for those external distributions.

Python, Blender/bpy, NumPy/OpenImageIO/OpenColorIO, FFmpeg/FFprobe, codec and
GPU components also retain their own licenses. This release does not certify
the license closure of an external binary distribution. Redistributing an
environment, wheel or binary requires review of that actual payload and its
dependency notices, beyond this source-only release.

Public original fixture scripts create their own local test data. They grant
no rights over unrelated third-party assets. Local production assets, private
audit jobs, profiles, receipts, credentials, Wiki and working-memory records
are excluded from the release.

# Compositing Workflow 0.8.0

Experimental source-only Blender extension. The source manifest declares
GPL-3.0-or-later; LICENSE contains the complete reviewed GPLv3 text.
No model, media, compute runtime, CLI, dependency binary or third-party asset
rights are supplied by this ZIP. Model and dependency licenses remain separate.

Relight requires a matching external blenderctl source tree and an explicitly
approved compute environment. Select its root (containing tools/blenderctl)
in extension preferences, or set BLENDERCTL_ROOT. The source-tree sibling is
the final fallback. Explicit invalid roots fail without silently falling back.
Restart Blender after changing source roots to avoid global module conflicts.
Establish an external guarded live session before selecting its ready JSON.
The extension does not install dependencies or start the compute session.

The native package contains exactly eleven source/document members. Adjacent
package-index.json records their sizes, SHA-256 and original source identities.
Installation, GUI, preference persistence, live bind and image validation are
separate acceptance steps; a successful build alone does not certify them.

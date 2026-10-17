"""Build the source-only Compositing Workflow native extension with stdlib.

No download, dependency installation, Blender startup or preference changes.
The destination directory must be new; no existing output is overwritten.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tomllib
import zipfile


SOURCE_MEMBERS = (
    "__init__.py", "blender_manifest.toml", "contract.py", "core.py",
    "depth_contract.py", "depth_estimate_contract.py", "depth_math.py",
    "movie_contract.py", "relight_preview_ui.py",
)
MEMBERS = tuple(sorted((*SOURCE_MEMBERS, "LICENSE", "README.md")))
GPL3_SHA256 = "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive_bytes(payloads: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in MEMBERS:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 17, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payloads[name])
    return buffer.getvalue()


def build(source_root: Path, license_source: Path, output_dir: Path) -> dict:
    root = source_root.resolve(strict=True)
    source = root / "tools/compositing_workflow_addon"
    license_path = license_source.resolve(strict=True)
    destination = output_dir.resolve()
    if destination.exists():
        raise FileExistsError(f"Output directory already exists: {destination}")
    before = {}
    for name in SOURCE_MEMBERS:
        path = (source / name).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Source member must be a file inside source root: {name}")
        before[name] = path.read_bytes()
        if name.endswith(".py"):
            ast.parse(before[name], filename=name)
    license_data = license_path.read_bytes()
    if sha256(license_data) != GPL3_SHA256:
        raise ValueError("GPLv3 LICENSE must match the reviewed complete text; a notice is insufficient")
    manifest = tomllib.loads(before["blender_manifest.toml"].decode("utf-8"))
    version = manifest.get("version", "")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Expected an explicit major.minor.patch extension version")
    if manifest.get("id") != "compositing_workflow_addon":
        raise ValueError("Unexpected extension id")
    if manifest.get("license") != ["SPDX:GPL-3.0-or-later"]:
        raise ValueError("Unexpected extension license declaration")
    init = ast.parse(before["__init__.py"])
    info = next(ast.literal_eval(node.value) for node in init.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets))
    if info.get("version") != tuple(int(part) for part in version.split(".")):
        raise ValueError("bl_info and native manifest versions disagree")
    readme = f"""# Compositing Workflow {version}

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
""".encode("utf-8")
    payloads = {**before, "LICENSE": license_data, "README.md": readme}
    payload = archive_bytes(payloads)
    if payload != archive_bytes(payloads):
        raise RuntimeError("Deterministic same-input archive check failed")
    members = []
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if archive.namelist() != list(MEMBERS) or archive.testzip() is not None:
            raise RuntimeError("Archive whitelist or CRC validation failed")
        for name in MEMBERS:
            data = archive.read(name)
            if data != payloads[name]:
                raise RuntimeError(f"Archive member readback mismatch: {name}")
            origin = ("tools/compositing_workflow_addon/" + name if name in SOURCE_MEMBERS
                      else "reviewed-complete-GPLv3-text" if name == "LICENSE" else "generated-by-native-builder")
            members.append({"file": name, "bytes": len(data), "sha256": sha256(data), "source": origin})
    for name, data in before.items():
        if (source / name).read_bytes() != data:
            raise RuntimeError(f"Source changed during build; refusing publication: {name}")
    if license_path.read_bytes() != license_data:
        raise RuntimeError("License source changed during build")
    archive_name = f"compositing-workflow-{version}-native.zip"
    report = {
        "schema": "compositing-native-extension-package-v1", "version": version,
        "status": "built_unpublished", "zip_file": archive_name,
        "zip_sha256": sha256(payload), "zip_bytes": len(payload),
        "whitelist": list(MEMBERS), "members": members,
        "source_identity": [{"file": "tools/compositing_workflow_addon/" + name,
                             "bytes": len(data), "sha256": sha256(data)} for name, data in before.items()],
        "build_script_sha256": sha256(Path(__file__).read_bytes()),
        "license_source_sha256": sha256(license_data), "sources_unchanged_during_build": True,
        "deterministic_repeat_equal": True, "all_archive_members_readback_equal": True,
        "excluded": ["CLI", "runtime", "weights", "models", "media", "assets", "private-config", "pyc", "pyo", "__pycache__"],
        "acceptance": {"official_validation": "not_run_by_builder", "installation": "not_run_by_builder",
                       "gui": "not_run_by_builder", "live_session": "not_run_by_builder"},
    }
    destination.mkdir(parents=True, exist_ok=False)
    with (destination / archive_name).open("xb") as stream:
        stream.write(payload)
    with (destination / "package-index.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    if sha256((destination / archive_name).read_bytes()) != report["zip_sha256"]:
        raise RuntimeError("Final archive file SHA mismatch")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path, help="Matching tree containing tools/compositing_workflow_addon")
    parser.add_argument("--license-source", required=True, type=Path, help="Existing full GPLv3 LICENSE, checked against reviewed SHA-256")
    parser.add_argument("--output-dir", required=True, type=Path, help="New destination directory; never overwritten")
    args = parser.parse_args()
    try:
        report = build(args.source_root, args.license_source, args.output_dir)
    except (OSError, ValueError, RuntimeError, StopIteration, SyntaxError) as exc:
        print(f"Native extension build failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "version": report["version"],
                      "zip": str(args.output_dir.resolve() / report["zip_file"]),
                      "zip_sha256": report["zip_sha256"], "members": len(report["members"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

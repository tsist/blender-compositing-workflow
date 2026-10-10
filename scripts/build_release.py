"""Build deterministic source-only release ZIPs from an explicit inventory."""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
from verify_release import (ADDON, ADDON_FILES, ROOT, load_publication,
                            release_files, safe_file, sha, verify)


def archive(entries: list[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    # Stored entries avoid zlib-version variation; timestamp and permissions are fixed.
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as output:
        for name, data in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            output.writestr(info, data)
    return buffer.getvalue()


def build(root: Path = ROOT) -> dict:
    validation = verify(root)
    publication = load_publication(root)
    version = publication["release"]
    names = release_files(publication)
    source = [(name, safe_file(root, name).read_bytes()) for name in names]
    native = [(name, safe_file(root, ADDON + name).read_bytes()) for name in ADDON_FILES]
    prefix = "skills/"
    skill = [(name[len(prefix):], data) for name, data in source if name.startswith(prefix)]
    skill.append(("LICENSE", safe_file(root, "LICENSE").read_bytes()))
    bundles = {
        "compositing_workflow_addon-" + version + ".zip": native,
        "blender-compositing-skill-" + version + ".zip": skill,
        "blender-compositing-workflow-" + version + "-source.zip": source,
    }
    dist = root / "dist"
    if dist.is_symlink():
        raise ValueError("Refusing symlink dist directory")
    dist.mkdir(exist_ok=True)
    hashes = []
    for name, entries in bundles.items():
        data = archive(entries)
        if data != archive(entries):
            raise ValueError("Archive reproducibility failure: " + name)
        target = dist / name
        if target.exists() and target.read_bytes() != data:
            raise ValueError("Refusing to overwrite different existing release artifact: " + name)
        if not target.exists():
            target.write_bytes(data)
        # Verify every archive entry against the exact source bytes after writing.
        with zipfile.ZipFile(target) as check:
            if check.namelist() != sorted(n for n, _ in entries):
                raise ValueError("Archive inventory mismatch: " + name)
            for entry, expected in entries:
                if check.read(entry) != expected:
                    raise ValueError("Archive entry byte mismatch: " + entry)
        hashes.append((name, sha(data), len(entries), len(data)))
    sums = "".join(digest + "  " + name + "\n" for name, digest, _, _ in sorted(hashes))
    checksum = dist / "SHA256SUMS"
    if checksum.exists() and checksum.read_bytes() != sums.encode():
        raise ValueError("Refusing to overwrite different SHA256SUMS")
    if not checksum.exists():
        checksum.write_bytes(sums.encode())
    return {"status": "passed_deterministic_release_build", "validation": validation,
            "artifacts": [{"file": "dist/" + name, "sha256": digest,
                           "entries": count, "bytes": size} for name, digest, count, size in hashes],
            "checksums": "dist/SHA256SUMS", "scope": "Source-only archives; external runtimes and production assets excluded"}


if __name__ == "__main__":
    try:
        print(json.dumps(build(), indent=2))
    except (ValueError, OSError, KeyError, SyntaxError, TypeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        sys.exit(1)

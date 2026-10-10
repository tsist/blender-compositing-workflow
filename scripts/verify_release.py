"""Verify the public source inventory without importing or running Blender code."""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ADDON = "tools/compositing_workflow_addon/"
ADDON_FILES = ("__init__.py", "contract.py", "core.py", "movie_contract.py",
               "blender_manifest.toml", "LICENSE.txt")
REFERENCE_PAIRS = {
    "usage": "USAGE", "contract": "CONTRACT", "validation": "VALIDATION",
    "dependencies": "DEPENDENCIES", "color-hdr": "COLOR-HDR",
}
FIXED_FILES = {
    ".gitattributes", ".gitignore", "LICENSE", "PUBLICATION.json",
    "README.md", "README.zh-CN.md", "blenderctl.ps1",
    "docs/USAGE.md", "docs/CONTRACT.md", "docs/VALIDATION.md",
    "docs/DEPENDENCIES.md", "docs/COLOR-HDR.md", "docs/LICENSING.md",
    "docs/SKILLS.md", "skills/blender-compositing/SKILL.md",
    "examples/create_fixture.py", "examples/make_request.py",
    "scripts/verify_release.py", "scripts/build_release.py",
    ".github/workflows/verify.yml",
    *("skills/blender-compositing/references/" + name + ".md"
      for name in REFERENCE_PAIRS),
    *(ADDON + name for name in ADDON_FILES),
}
BLOCKED_PARTS = {".git", "runtime", "audit", "__pycache__", ".venv"}
TEXT_SUFFIXES = {".py", ".json", ".md", ".txt", ".toml", ".ps1", ".yml"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_file(root: Path, name: str) -> Path:
    """Inventory entries must be regular, internal, relative POSIX paths."""
    pure = PurePosixPath(name)
    if (not name or "\\" in name or pure.is_absolute() or ":" in name
            or any(part in BLOCKED_PARTS or part in {"", ".."} for part in pure.parts)):
        raise ValueError("Unsafe publication path: " + name)
    path = root.joinpath(*pure.parts)
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Missing or non-regular publication file: " + name)
    if path.suffix not in TEXT_SUFFIXES and name not in FIXED_FILES:
        raise ValueError("Unexpected publication file type: " + name)
    return path


def load_publication(root: Path) -> dict:
    return json.loads((root / "PUBLICATION.json").read_text(encoding="utf-8-sig"))


def publication_rows(publication: dict) -> list[dict]:
    rows = []
    for key in ("runtime_documents", "schema_documents", "support_documents"):
        values = publication.get(key)
        if not isinstance(values, list) or not values:
            raise ValueError("Required non-empty inventory: " + key)
        rows.extend(values)
    # Sanitized capabilities are tracked separately from the runtime identity.
    public = publication.get("public_documents")
    if not isinstance(public, list) or not public:
        raise ValueError("Missing public document inventory")
    rows.extend(public)
    return rows


def release_files(publication: dict) -> list[str]:
    return sorted(FIXED_FILES | {row["file"] for row in publication_rows(publication)})


def private_findings(text: str) -> list[str]:
    """Target actual private identifiers, not generic Windows path examples."""
    normalized = text.replace("\\\\", "/").replace("\\", "/").lower()
    findings = []
    if ("173" + "99") in normalized:
        findings.append("private user identifier")
    if ("f:" + "/blender ai") in normalized:
        findings.append("private project root")
    private_paths = (r"wm-20\d\d-\d\d-\d\d-[a-z]|" + "runtime" + "/audit/|"
                     + re.escape("/." + "dsh/memory-lancedb-pro/") + "|"
                     + re.escape("/." + "codex/") + r"(?:plugins|visualizations)/")
    if re.search(private_paths, normalized):
        findings.append("private task/audit/store path")
    token_patterns = (
        r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}",
        r"sk-[A-Za-z0-9_-]{32,}", r"AKIA[A-Z0-9]{16}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    )
    if any(re.search(pattern, text) for pattern in token_patterns):
        findings.append("credential-shaped value")
    return findings


def verify(root: Path = ROOT) -> dict:
    publication = load_publication(root)
    rows = publication_rows(publication)
    seen = {}
    for row in rows:
        name = row["file"]
        expected = row.get("expected_sha256", row.get("sha256"))
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("Invalid SHA descriptor: " + name)
        if name in seen and seen[name] != expected:
            raise ValueError("Conflicting inventory SHA: " + name)
        seen[name] = expected
        if sha(safe_file(root, name).read_bytes()) != expected:
            raise ValueError("Publication SHA mismatch: " + name)

    paths = set((root / "tools/blenderctl").glob("*.py"))
    paths.update((root / ADDON).glob("*.py"))
    paths.add(root / ADDON / "blender_manifest.toml")
    runtime = [{"file": path.relative_to(root).as_posix(),
                "expected_sha256": sha(path.read_bytes())} for path in sorted(paths)]
    if len(runtime) != 177 or runtime != publication["runtime_documents"]:
        raise ValueError("Runtime inventory differs from the original 177-file source algorithm")
    identity = sha(json.dumps(runtime, sort_keys=True, separators=(",", ":")).encode())
    if identity != publication["runtime_identity"]:
        raise ValueError("Compositing implementation identity mismatch")
    actual_schemas = {path.relative_to(root).as_posix()
                      for path in (root / "docs/cli/schemas").glob("*.json")}
    if actual_schemas != {row["file"] for row in publication["schema_documents"]}:
        raise ValueError("Schema directory inventory mismatch")

    names = release_files(publication)
    counts = {"python_ast": 0, "json_parse": 0, "text_privacy_scan": 0}
    for name in names:
        path = safe_file(root, name)
        text = path.read_text(encoding="utf-8-sig")
        findings = private_findings(text)
        if findings:
            raise ValueError("Private content in " + name + ": " + ", ".join(findings))
        counts["text_privacy_scan"] += 1
        if path.suffix == ".py":
            ast.parse(text, filename=name)
            counts["python_ast"] += 1
        elif path.suffix == ".json":
            json.loads(text)
            counts["json_parse"] += 1
    for name, source in REFERENCE_PAIRS.items():
        if ((root / "docs" / (source + ".md")).read_bytes()
                != (root / "skills/blender-compositing/references" / (name + ".md")).read_bytes()):
            raise ValueError("Skill reference differs from public source: " + name)
    skill = (root / "skills/blender-compositing/SKILL.md").read_text(encoding="utf-8-sig")
    if not skill.startswith("---") or not re.search(r"^name: blender-compositing\s*$", skill, re.M):
        raise ValueError("Invalid public skill frontmatter")
    for ref in re.findall(r"\]\((references/[^)]+)\)", skill):
        safe_file(root, "skills/blender-compositing/" + ref)
    if publication["runtime_identity"] not in skill:
        raise ValueError("Public skill omits its runtime identity")
    return {"status": "passed_static_release_checks", "runtime_files": len(runtime),
            "runtime_identity": identity, "hashed_inventory_files": len(seen),
            "release_files": len(names), "reference_pairs": len(REFERENCE_PAIRS),
            **counts, "scope": "Hashes, AST/JSON, public navigation and targeted privacy checks; no runtime or visual certification"}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), indent=2))
    except (ValueError, OSError, KeyError, SyntaxError, TypeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        sys.exit(1)

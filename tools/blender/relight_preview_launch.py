"""Explicit factory-GUI entry for one existing public relight hot session.

Use Blender --factory-startup --disable-autoexec --python this_file --
ABS/session-ready.json --audit-output ABS/new-launch-receipt.json.
No external worker is started here; the real SessionClient validates authority.
"""
import argparse
import json
import os
from pathlib import Path
import sys


def arguments(argv):
    parser = argparse.ArgumentParser(
        description="Bind an existing live relight session to a fresh owned GUI preview.",
        allow_abbrev=False,
    )
    parser.add_argument("session_ready", help="One absolute existing session-ready.json")
    parser.add_argument(
        "--audit-output", required=True,
        help="Explicit absolute NEW JSON receipt; parent directory must already exist",
    )
    args = parser.parse_args(argv)
    ready = Path(args.session_ready)
    output = Path(args.audit_output)
    if not ready.is_absolute() or ready.name != "session-ready.json" or not ready.is_file():
        parser.error("session_ready must be one absolute existing session-ready.json")
    if not output.is_absolute() or output.suffix.lower() != ".json":
        parser.error("--audit-output must be an absolute new .json file")
    if output.exists() or not output.parent.is_dir():
        parser.error("--audit-output must not exist and its parent directory must exist")
    return ready.resolve(), output.resolve()


def main(argv):
    ready, output = arguments(argv)
    # Reserve the receipt before editing the owned GUI. Exclusive creation also
    # protects against a concurrent caller winning after the argument preflight.
    with output.open("x", encoding="utf-8") as receipt:
        record = {
            "schema": "relight-preview-launch-v1",
            "status": "starting",
            "session_ready": str(ready),
            "audit_output": str(output),
            "pid": os.getpid(),
            "acceptance": "real_gpu_final_not_run_by_launcher",
        }
        try:
            import bpy
            if bpy.app.background:
                raise RuntimeError("A factory-startup interactive Blender GUI is required")
            tools = Path(__file__).resolve().parent.parent
            sys.dont_write_bytecode = True
            sys.path.insert(0, str(tools))
            import compositing_workflow_addon as package
            expected = tools / "compositing_workflow_addon" / "__init__.py"
            if Path(package.__file__).resolve() != expected.resolve():
                raise RuntimeError("A different compositing_workflow_addon is already loaded; use a fresh factory instance")
            from compositing_workflow_addon import relight_preview_ui as ui
            package.register()
            # No client_factory override: production SessionClient performs the
            # ready/request/launch/producer/live-heartbeat checks. No Torch here.
            scene = ui.setup(str(ready), open_window=True)
            owner = scene[ui.OWNER]
            runtime = ui._sessions[owner]
            window_pointer = runtime.get("window_pointer")
            if window_pointer is None:
                raise RuntimeError("Owned preview window was not created")
            record.update({
                "status": "ui_started_unverified",
                "file": bpy.data.filepath,
                "scene": scene.name,
                "scene_pointer": scene.as_pointer(),
                "owner": owner,
                "window_pointer": window_pointer,
                "addon_file": str(expected.resolve()),
                "blender_version": bpy.app.version_string,
            })
        except BaseException as exc:
            record.update({"status": "failed", "error": f"{type(exc).__name__}: {exc}"})
            json.dump(record, receipt, ensure_ascii=False, indent=2, allow_nan=False)
            receipt.flush()
            raise
        json.dump(record, receipt, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps(record, ensure_ascii=False, allow_nan=False), flush=True)
    return record


if __name__ == "__main__":
    # Only arguments following Blender's explicit separator are accepted. This
    # entry never accepts expressions, Python files, templates, or arbitrary code.
    if "--" not in sys.argv:
        raise SystemExit("Pass -- ABS/session-ready.json --audit-output ABS/new-launch-receipt.json")
    main(sys.argv[sys.argv.index("--") + 1:])

#!/usr/bin/env python3
"""Validate a compact physical-run evidence manifest and optional file checksums."""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import yaml

REQUIRED = ("run_id", "date", "robot_id", "operator", "environment", "hardware_profile", "rosbag", "preflight", "tf_audit", "mapping")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def lint(data: dict, base: Path, check_files: bool = False) -> list[str]:
    errors: list[str] = []
    run = data.get("hardware_run")
    if not isinstance(run, dict):
        return ["missing hardware_run mapping"]
    for key in REQUIRED:
        if run.get(key) in (None, "", {}):
            errors.append(f"missing required run field: {key}")
    if run.get("simulation") is not False:
        errors.append("hardware_run.simulation must be false")
    if check_files:
        for key in ("hardware_profile", "rosbag", "preflight", "tf_audit"):
            rel = run.get(key)
            if rel and not (base / rel).exists():
                errors.append(f"missing required evidence path: {rel}")
        for item in run.get("files", []):
            rel = item.get("path")
            if not rel:
                errors.append("file entry missing path")
                continue
            path = (base / rel).resolve()
            if not path.exists():
                errors.append(f"missing evidence file: {rel}")
                continue
            expected = item.get("sha256")
            if expected and sha256(path) != expected:
                errors.append(f"sha256 mismatch: {rel}")
    return errors


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    p.add_argument("--check-files", action="store_true")
    args = p.parse_args()
    data = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    errors = lint(data, args.manifest.parent, args.check_files)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        raise SystemExit(1)
    print("hardware evidence manifest: PASS")


if __name__ == "__main__":
    main()

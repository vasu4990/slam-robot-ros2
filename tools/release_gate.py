#!/usr/bin/env python3
from pathlib import Path
import argparse, yaml

ROOT = Path(__file__).resolve().parents[1]

def evaluate(stage: str, root: Path = ROOT) -> tuple[bool, list[str]]:
    validation = yaml.safe_load((root / "config/robot.yaml").read_text())["validation"]
    maturity = yaml.safe_load((root / "config/validation.yaml").read_text())["maturity"]
    required = maturity[stage]["required"]
    missing = [key for key in required if not validation.get(key, False)]
    return not missing, missing

def main():
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=[
        "reference", "ros-build-ready", "simulation-validated",
        "hardware-mapping-validated", "hardware-localization-validated"
    ])
    args = p.parse_args()
    ok, missing = evaluate(args.stage)
    print(f"stage={args.stage} passed={str(ok).lower()}")
    if missing:
        print("missing: " + ", ".join(missing))
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()

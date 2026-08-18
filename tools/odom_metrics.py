#!/usr/bin/env python3
"""Analyze a CSV odometry trace exported as stamp_sec,x_m,y_m,yaw_rad."""
from __future__ import annotations
from pathlib import Path
import argparse, csv, json, math

def angular_distance(a: float, b: float) -> float:
    return abs((a - b + math.pi) % (2 * math.pi) - math.pi)

def summarize(path: Path) -> dict:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({k: float(v) for k, v in row.items()})
    if len(rows) < 2:
        raise ValueError("at least two odometry samples are required")
    distances, yaw_steps, dts = [], [], []
    for a, b in zip(rows, rows[1:]):
        distances.append(math.hypot(b["x_m"] - a["x_m"], b["y_m"] - a["y_m"]))
        yaw_steps.append(angular_distance(b["yaw_rad"], a["yaw_rad"]))
        dts.append(b["stamp_sec"] - a["stamp_sec"])
    positive_dts = [dt for dt in dts if dt > 0]
    if len(positive_dts) != len(dts):
        raise ValueError("timestamps must be strictly increasing")
    duration = rows[-1]["stamp_sec"] - rows[0]["stamp_sec"]
    return {
        "samples": len(rows),
        "duration_sec": duration,
        "mean_rate_hz": (len(rows) - 1) / duration if duration > 0 else 0.0,
        "path_length_m": sum(distances),
        "max_translation_step_m": max(distances),
        "max_yaw_step_rad": max(yaw_steps),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = summarize(a.csv)
    text = json.dumps(result, indent=2)
    print(text)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text + "\n")

if __name__ == "__main__":
    main()
